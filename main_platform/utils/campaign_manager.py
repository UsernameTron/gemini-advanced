"""
Campaign Management Utilities
Handles campaign creation, storage, analytics, and export functionality
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib
import zipfile
import io
import base64

class CampaignDatabase:
    """Simple SQLite database for campaign storage"""
    
    def __init__(self, db_path: str = "campaigns.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    brand_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analysis_data TEXT,
                    generated_images TEXT,
                    status TEXT DEFAULT 'active',
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT,
                    event_type TEXT,
                    event_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
                )
            """)
    
    def save_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Save campaign data and return campaign ID"""
        campaign_id = self._generate_campaign_id(campaign_data)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO campaigns 
                (id, brand_name, analysis_data, generated_images, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                campaign_id,
                campaign_data.get('brand_name', ''),
                json.dumps(campaign_data.get('analysis_data', {})),
                json.dumps(campaign_data.get('generated_images', [])),
                json.dumps(campaign_data.get('metadata', {}))
            ))
        
        return campaign_id
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve campaign by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM campaigns WHERE id = ?", (campaign_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'brand_name': row['brand_name'],
                    'created_at': row['created_at'],
                    'analysis_data': json.loads(row['analysis_data'] or '{}'),
                    'generated_images': json.loads(row['generated_images'] or '[]'),
                    'status': row['status'],
                    'metadata': json.loads(row['metadata'] or '{}')
                }
        
        return None
    
    def list_campaigns(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent campaigns"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, brand_name, created_at, status 
                FROM campaigns 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _generate_campaign_id(self, campaign_data: Dict[str, Any]) -> str:
        """Generate unique campaign ID"""
        content = f"{campaign_data.get('brand_name', '')}{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

class CampaignManager:
    """High-level campaign management with analytics and export capabilities"""
    
    def __init__(self, config):
        self.config = config
        self.db = CampaignDatabase()
        self.analytics = CampaignAnalytics(self.db)
    
    def create_campaign(self, brand_name: str, analysis_data: Dict[str, Any], 
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new campaign"""
        campaign_data = {
            'brand_name': brand_name,
            'analysis_data': analysis_data,
            'generated_images': [],
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat()
        }
        
        campaign_id = self.db.save_campaign(campaign_data)
        
        # Log campaign creation
        self.analytics.log_event(campaign_id, 'campaign_created', {
            'brand_name': brand_name,
            'analysis_vectors': analysis_data.get('brand_analysis', {}).get('vectors', [])
        })
        
        return campaign_id
    
    def add_generated_image(self, campaign_id: str, image_data: Dict[str, Any]):
        """Add a generated image to campaign"""
        campaign = self.db.get_campaign(campaign_id)
        if campaign:
            campaign['generated_images'].append({
                **image_data,
                'added_at': datetime.now().isoformat()
            })
            self.db.save_campaign(campaign)
            
            # Log image generation
            self.analytics.log_event(campaign_id, 'image_generated', {
                'generation_time': image_data.get('generation_metadata', {}).get('generation_time', 0),
                'cost': image_data.get('generation_metadata', {}).get('cost', 0)
            })
    
    def export_campaign(self, campaign_id: str, format: str = 'json') -> bytes:
        """Export campaign data in specified format"""
        campaign = self.db.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if format == 'json':
            return self._export_json(campaign)
        elif format == 'zip':
            return self._export_zip(campaign)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, campaign: Dict[str, Any]) -> bytes:
        """Export campaign as JSON"""
        export_data = {
            'campaign_export': campaign,
            'export_timestamp': datetime.now().isoformat(),
            'platform': 'Brand Deconstruction Platform',
            'version': '1.0'
        }
        return json.dumps(export_data, indent=2).encode('utf-8')
    
    def _export_zip(self, campaign: Dict[str, Any]) -> bytes:
        """Export campaign as ZIP with images and data"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add campaign data as JSON
            campaign_json = self._export_json(campaign)
            zip_file.writestr('campaign_data.json', campaign_json)
            
            # Add generated images
            for i, image_data in enumerate(campaign.get('generated_images', [])):
                if 'image_base64' in image_data:
                    image_bytes = base64.b64decode(image_data['image_base64'])
                    zip_file.writestr(f'generated_image_{i+1}.png', image_bytes)
            
            # Add analysis summary
            analysis_summary = self._create_analysis_summary(campaign)
            zip_file.writestr('analysis_summary.txt', analysis_summary)
        
        zip_buffer.seek(0)
        return zip_buffer.read()
    
    def _create_analysis_summary(self, campaign: Dict[str, Any]) -> str:
        """Create human-readable analysis summary"""
        analysis_data = campaign.get('analysis_data', {})
        brand_analysis = analysis_data.get('brand_analysis', {})
        
        summary = f"""
Brand Deconstruction Analysis Summary
=====================================

Brand: {campaign.get('brand_name', 'Unknown')}
Generated: {campaign.get('created_at', 'Unknown')}

Analysis Overview:
{json.dumps(brand_analysis.get('intelligence_data', {}), indent=2)}

Vulnerability Assessment:
{json.dumps(brand_analysis.get('vulnerability_analysis', {}), indent=2)}

Satirical Concepts Generated: {len(brand_analysis.get('satirical_concepts', []))}
Images Generated: {len(campaign.get('generated_images', []))}

Campaign Statistics:
- Total Cost: ${sum(img.get('generation_metadata', {}).get('cost', 0) for img in campaign.get('generated_images', []))}
- Average Generation Time: {sum(img.get('generation_metadata', {}).get('generation_time', 0) for img in campaign.get('generated_images', [])) / max(len(campaign.get('generated_images', [])), 1):.2f}s

Generated by Brand Deconstruction Platform v1.0
        """.strip()
        
        return summary

class CampaignAnalytics:
    """Analytics and reporting for campaigns"""
    
    def __init__(self, database: CampaignDatabase):
        self.db = database
    
    def log_event(self, campaign_id: str, event_type: str, event_data: Dict[str, Any]):
        """Log an analytics event"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute("""
                INSERT INTO analytics (campaign_id, event_type, event_data)
                VALUES (?, ?, ?)
            """, (campaign_id, event_type, json.dumps(event_data)))
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get overall platform usage statistics"""
        with sqlite3.connect(self.db.db_path) as conn:
            # Total campaigns
            total_campaigns = conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]
            
            # Total images generated
            total_images = conn.execute("""
                SELECT COUNT(*) FROM analytics WHERE event_type = 'image_generated'
            """).fetchone()[0]
            
            # Unique brands analyzed
            unique_brands = conn.execute("""
                SELECT COUNT(DISTINCT brand_name) FROM campaigns
            """).fetchone()[0]
            
            # Recent activity (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            recent_campaigns = conn.execute("""
                SELECT COUNT(*) FROM campaigns WHERE created_at > ?
            """, (thirty_days_ago,)).fetchone()[0]
            
            # Cost analysis
            cost_data = conn.execute("""
                SELECT event_data FROM analytics WHERE event_type = 'image_generated'
            """).fetchall()
            
            total_cost = 0.0
            for row in cost_data:
                try:
                    data = json.loads(row[0])
                    total_cost += data.get('cost', 0)
                except:
                    continue
            
            return {
                'total_campaigns': total_campaigns,
                'total_images_generated': total_images,
                'unique_brands_analyzed': unique_brands,
                'recent_campaigns_30d': recent_campaigns,
                'total_generation_cost': total_cost,
                'average_cost_per_campaign': total_cost / max(total_campaigns, 1),
                'last_updated': datetime.now().isoformat()
            }
