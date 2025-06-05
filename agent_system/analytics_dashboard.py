"""
Data Analytics Dashboard Module
Independent functionality for the unified Meld & RAG system
Provides comprehensive data analytics and visualization capabilities
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from flask import Blueprint, render_template, request, jsonify, session
import sqlite3
import os

@dataclass
class AnalyticsData:
    """Data structure for analytics information."""
    metric_name: str
    value: float
    timestamp: datetime
    category: str
    metadata: Dict[str, Any] = None

@dataclass
class ChartConfig:
    """Configuration for chart generation."""
    chart_type: str  # 'line', 'bar', 'pie', 'scatter', 'heatmap'
    title: str
    x_axis: str
    y_axis: str
    color_scheme: str = 'viridis'
    height: int = 400

class DataAnalyticsDashboard:
    """Main class for data analytics dashboard functionality."""
    
    def __init__(self, app=None, data_dir: str = "/app/data"):
        self.app = app
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "analytics.db")
        self._init_database()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the dashboard with Flask app."""
        self.app = app
        self._register_routes()
    
    def _init_database(self):
        """Initialize SQLite database for analytics data."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analytics data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                category TEXT NOT NULL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create system metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                active_sessions INTEGER,
                requests_per_minute REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create user activity table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                action_type TEXT,
                agent_type TEXT,
                execution_time REAL,
                success BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _register_routes(self):
        """Register all dashboard routes."""
        
        @self.app.route('/analytics-dashboard')
        def analytics_dashboard():
            """Main analytics dashboard page."""
            return render_template('analytics_dashboard.html')
        
        @self.app.route('/api/analytics/overview')
        def get_analytics_overview():
            """Get overview analytics data."""
            try:
                overview_data = self._get_overview_metrics()
                return jsonify({
                    'success': True,
                    'data': overview_data
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/analytics/charts/<chart_type>')
        def get_chart_data(chart_type):
            """Get data for specific chart types."""
            try:
                timeframe = request.args.get('timeframe', '24h')
                data = self._get_chart_data(chart_type, timeframe)
                return jsonify({
                    'success': True,
                    'data': data
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/analytics/custom-query', methods=['POST'])
        def custom_analytics_query():
            """Execute custom analytics queries."""
            try:
                query_config = request.get_json()
                result = self._execute_custom_query(query_config)
                return jsonify({
                    'success': True,
                    'data': result
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/analytics/export/<format>')
        def export_analytics_data(format):
            """Export analytics data in various formats."""
            try:
                timeframe = request.args.get('timeframe', '7d')
                data_type = request.args.get('type', 'all')
                
                exported_data = self._export_data(format, timeframe, data_type)
                return jsonify({
                    'success': True,
                    'data': exported_data
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/analytics/real-time')
        def real_time_metrics():
            """Get real-time system metrics."""
            try:
                metrics = self._get_real_time_metrics()
                return jsonify({
                    'success': True,
                    'data': metrics
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
    
    def record_user_activity(self, session_id: str, action_type: str, 
                           agent_type: str = None, execution_time: float = None, 
                           success: bool = True):
        """Record user activity for analytics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activity 
                (session_id, action_type, agent_type, execution_time, success)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, action_type, agent_type, execution_time, success))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to record user activity: {e}")
    
    def record_system_metrics(self, cpu_usage: float, memory_usage: float, 
                            disk_usage: float, active_sessions: int, 
                            requests_per_minute: float):
        """Record system performance metrics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (cpu_usage, memory_usage, disk_usage, active_sessions, requests_per_minute)
                VALUES (?, ?, ?, ?, ?)
            ''', (cpu_usage, memory_usage, disk_usage, active_sessions, requests_per_minute))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to record system metrics: {e}")
    
    def _get_overview_metrics(self) -> Dict[str, Any]:
        """Get overview metrics for the dashboard."""
        conn = sqlite3.connect(self.db_path)
        
        # Total sessions today
        today = datetime.now().date()
        total_sessions = pd.read_sql_query('''
            SELECT COUNT(DISTINCT session_id) as count
            FROM user_activity 
            WHERE DATE(timestamp) = ?
        ''', conn, params=[today]).iloc[0]['count']
        
        # Total agent interactions
        total_interactions = pd.read_sql_query('''
            SELECT COUNT(*) as count
            FROM user_activity 
            WHERE action_type = 'agent_interaction'
            AND DATE(timestamp) = ?
        ''', conn, params=[today]).iloc[0]['count']
        
        # Average response time
        avg_response_time = pd.read_sql_query('''
            SELECT AVG(execution_time) as avg_time
            FROM user_activity 
            WHERE execution_time IS NOT NULL
            AND DATE(timestamp) = ?
        ''', conn, params=[today]).iloc[0]['avg_time'] or 0
        
        # Success rate
        success_rate = pd.read_sql_query('''
            SELECT 
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as rate
            FROM user_activity 
            WHERE DATE(timestamp) = ?
        ''', conn, params=[today]).iloc[0]['rate'] or 0
        
        # Popular agents
        popular_agents = pd.read_sql_query('''
            SELECT agent_type, COUNT(*) as usage_count
            FROM user_activity 
            WHERE agent_type IS NOT NULL
            AND DATE(timestamp) = ?
            GROUP BY agent_type
            ORDER BY usage_count DESC
            LIMIT 5
        ''', conn, params=[today])
        
        conn.close()
        
        return {
            'total_sessions': int(total_sessions),
            'total_interactions': int(total_interactions),
            'avg_response_time': round(avg_response_time, 3),
            'success_rate': round(success_rate, 1),
            'popular_agents': popular_agents.to_dict('records')
        }
    
    def _get_chart_data(self, chart_type: str, timeframe: str) -> Dict[str, Any]:
        """Get data for specific chart visualization."""
        conn = sqlite3.connect(self.db_path)
        
        # Parse timeframe
        if timeframe == '24h':
            since = datetime.now() - timedelta(hours=24)
        elif timeframe == '7d':
            since = datetime.now() - timedelta(days=7)
        elif timeframe == '30d':
            since = datetime.now() - timedelta(days=30)
        else:
            since = datetime.now() - timedelta(hours=24)
        
        if chart_type == 'activity_timeline':
            # Activity over time
            df = pd.read_sql_query('''
                SELECT 
                    DATE(timestamp) as date,
                    HOUR(timestamp) as hour,
                    COUNT(*) as activity_count
                FROM user_activity 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp), HOUR(timestamp)
                ORDER BY timestamp
            ''', conn, params=[since])
            
            if not df.empty:
                fig = px.line(df, x='hour', y='activity_count', 
                            title='User Activity Timeline')
                chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
            else:
                chart_json = json.dumps({})
        
        elif chart_type == 'agent_usage':
            # Agent usage distribution
            df = pd.read_sql_query('''
                SELECT agent_type, COUNT(*) as usage_count
                FROM user_activity 
                WHERE timestamp >= ? AND agent_type IS NOT NULL
                GROUP BY agent_type
                ORDER BY usage_count DESC
            ''', conn, params=[since])
            
            if not df.empty:
                fig = px.pie(df, values='usage_count', names='agent_type',
                           title='Agent Usage Distribution')
                chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
            else:
                chart_json = json.dumps({})
        
        elif chart_type == 'response_times':
            # Response time distribution
            df = pd.read_sql_query('''
                SELECT execution_time, agent_type
                FROM user_activity 
                WHERE timestamp >= ? AND execution_time IS NOT NULL
            ''', conn, params=[since])
            
            if not df.empty:
                fig = px.box(df, x='agent_type', y='execution_time',
                           title='Response Time Distribution by Agent')
                chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
            else:
                chart_json = json.dumps({})
        
        elif chart_type == 'success_rate':
            # Success rate over time
            df = pd.read_sql_query('''
                SELECT 
                    DATE(timestamp) as date,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                FROM user_activity 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', conn, params=[since])
            
            if not df.empty:
                fig = px.line(df, x='date', y='success_rate',
                            title='Success Rate Over Time')
                chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
            else:
                chart_json = json.dumps({})
        
        else:
            chart_json = json.dumps({})
        
        conn.close()
        
        return {
            'chart': chart_json,
            'data_points': len(df) if 'df' in locals() else 0
        }
    
    def _execute_custom_query(self, query_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom analytics queries."""
        conn = sqlite3.connect(self.db_path)
        
        query_type = query_config.get('type', 'simple')
        timeframe = query_config.get('timeframe', '24h')
        metrics = query_config.get('metrics', [])
        filters = query_config.get('filters', {})
        
        if timeframe == '24h':
            since = datetime.now() - timedelta(hours=24)
        elif timeframe == '7d':
            since = datetime.now() - timedelta(days=7)
        elif timeframe == '30d':
            since = datetime.now() - timedelta(days=30)
        else:
            since = datetime.now() - timedelta(hours=24)
        
        if query_type == 'agent_performance':
            query = '''
                SELECT 
                    agent_type,
                    COUNT(*) as total_requests,
                    AVG(execution_time) as avg_response_time,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                FROM user_activity 
                WHERE timestamp >= ? AND agent_type IS NOT NULL
                GROUP BY agent_type
                ORDER BY total_requests DESC
            '''
            df = pd.read_sql_query(query, conn, params=[since])
        
        elif query_type == 'user_patterns':
            query = '''
                SELECT 
                    HOUR(timestamp) as hour_of_day,
                    COUNT(*) as activity_count,
                    COUNT(DISTINCT session_id) as unique_users
                FROM user_activity 
                WHERE timestamp >= ?
                GROUP BY HOUR(timestamp)
                ORDER BY hour_of_day
            '''
            df = pd.read_sql_query(query, conn, params=[since])
        
        else:
            # Default query
            df = pd.read_sql_query('''
                SELECT * FROM user_activity 
                WHERE timestamp >= ?
                LIMIT 100
            ''', conn, params=[since])
        
        conn.close()
        
        return {
            'data': df.to_dict('records'),
            'columns': list(df.columns),
            'row_count': len(df)
        }
    
    def _export_data(self, format: str, timeframe: str, data_type: str) -> Dict[str, Any]:
        """Export analytics data in various formats."""
        conn = sqlite3.connect(self.db_path)
        
        if timeframe == '24h':
            since = datetime.now() - timedelta(hours=24)
        elif timeframe == '7d':
            since = datetime.now() - timedelta(days=7)
        elif timeframe == '30d':
            since = datetime.now() - timedelta(days=30)
        else:
            since = datetime.now() - timedelta(hours=24)
        
        if data_type == 'user_activity':
            df = pd.read_sql_query('''
                SELECT * FROM user_activity WHERE timestamp >= ?
            ''', conn, params=[since])
        elif data_type == 'system_metrics':
            df = pd.read_sql_query('''
                SELECT * FROM system_metrics WHERE timestamp >= ?
            ''', conn, params=[since])
        else:
            # Export all data
            df = pd.read_sql_query('''
                SELECT * FROM user_activity WHERE timestamp >= ?
            ''', conn, params=[since])
        
        conn.close()
        
        if format == 'json':
            return {
                'data': df.to_json(orient='records'),
                'filename': f'analytics_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        elif format == 'csv':
            return {
                'data': df.to_csv(index=False),
                'filename': f'analytics_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        else:
            return {
                'data': df.to_dict('records'),
                'filename': f'analytics_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
    
    def _get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics."""
        try:
            import psutil
            
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Record metrics
            self.record_system_metrics(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                active_sessions=len(session),  # Approximate
                requests_per_minute=0  # Would need to track this separately
            )
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'memory_available': memory.available // (1024**3),  # GB
                'disk_free': disk.free // (1024**3),  # GB
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            # Fallback if psutil not available
            return {
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'memory_available': 0,
                'disk_free': 0,
                'timestamp': datetime.now().isoformat(),
                'note': 'Real-time metrics unavailable (psutil not installed)'
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
