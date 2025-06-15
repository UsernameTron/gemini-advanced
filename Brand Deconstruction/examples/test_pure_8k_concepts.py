# File: examples/test_pure_8k_concepts.py

import asyncio
import os
import json
import sys
from pathlib import Path

# Add the parent directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from integrations.pure_8k_concept_pipeline import Pure8KConceptPipeline
from workflows.brand_deconstruction import CompleteBrandDeconstructionWorkflow

async def test_pure_8k_concept_development():
    """Test the pure GPT-4o 8K concept development system."""
    
    # Initialize workflow
    deconstruction_workflow = CompleteBrandDeconstructionWorkflow()
    
    # Get OpenAI API key
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    # Create pure 8K concept pipeline
    concept_pipeline = Pure8KConceptPipeline(
        deconstruction_workflow=deconstruction_workflow,
        openai_api_key=openai_api_key
    )
    
    # Test with target URL
    test_url = "https://salesforce.com"
    
    print("🎨 Testing Pure GPT-4o 8K Concept Development System")
    print("=" * 60)
    print(f"🎯 Target: {test_url}")
    print("🧠 Using GPT-4o for sophisticated 8K visual concept development")
    print("📐 No image generation - pure conceptual development")
    print("🎭 Focus: Professional satirical critique at ultra-high resolution")
    print("")
    
    # Test all analysis modes
    analysis_modes = [
        '8k_concept_development',
        'technical_specifications', 
        'creative_direction',
        'implementation_guide'
    ]
    
    result = await concept_pipeline.execute_concept_pipeline(
        url=test_url,
        analysis_modes=analysis_modes,
        include_alternatives=True
    )
    
    if result.success:
        print("✅ Pure 8K Concept Pipeline Completed Successfully!")
        print("=" * 60)
        
        # Display brand analysis summary
        brand_name = result.brand_deconstruction.brand_analysis.brand_name
        auth_score = result.brand_deconstruction.brand_analysis.authenticity_score
        vulnerabilities = result.brand_deconstruction.brand_analysis.satirical_vulnerabilities
        
        print(f"📊 Brand Analysis:")
        print(f"   🏢 Brand: {brand_name}")
        print(f"   🎯 Authenticity Score: {auth_score:.2f}")
        print(f"   🔍 Satirical Vulnerabilities: {len(vulnerabilities)}")
        print("")
        
        # Display concept developments
        if result.concept_developments:
            print(f"🎨 Visual Concepts Developed: {len(result.concept_developments)}")
            for i, concept in enumerate(result.concept_developments):
                print(f"\n   Concept {i+1}: {concept.concept_title}")
                print(f"   💡 Core Visual: {concept.visual_concept[:120]}...")
                if concept.alternative_concepts:
                    print(f"   🔄 Alternatives: {len(concept.alternative_concepts)} variations")
                if concept.satirical_strategy:
                    strategy_keys = list(concept.satirical_strategy.keys())[:3]
                    print(f"   🎭 Satirical Strategy: {', '.join(strategy_keys)}")
                print(f"   ⏱️  Development Time: {concept.processing_time:.2f}s")
        
        # Display technical specifications
        if result.technical_specifications:
            print(f"\n⚙️  Technical Specifications: {len(result.technical_specifications)}")
            for i, spec in enumerate(result.technical_specifications):
                print(f"   📐 Spec {i+1}: 8K UHD production requirements")
                if spec.technical_specifications:
                    spec_keys = list(spec.technical_specifications.keys())[:3]
                    print(f"   📋 Covers: {', '.join(spec_keys)}")
        
        # Display creative directions
        if result.creative_directions:
            print(f"\n🎬 Creative Directions: {len(result.creative_directions)}")
            for i, direction in enumerate(result.creative_directions):
                print(f"   🎨 Direction {i+1}: Artistic guidance provided")
                if direction.creative_direction:
                    direction_keys = list(direction.creative_direction.keys())[:3]
                    print(f"   📝 Includes: {', '.join(direction_keys)}")
        
        # Display implementation guides
        if result.implementation_guides:
            print(f"\n📋 Implementation Guides: {len(result.implementation_guides)}")
            for i, guide in enumerate(result.implementation_guides):
                print(f"   📖 Guide {i+1}: Step-by-step creation instructions")
                if guide.implementation_steps:
                    print(f"   📝 Steps: {len(guide.implementation_steps)} detailed instructions")
        
        # Display pipeline metadata
        metadata = result.pipeline_metadata
        print(f"\n📊 Pipeline Performance:")
        print(f"   ⏱️  Total Time: {metadata['total_processing_time']:.2f}s")
        print(f"   🧠 GPT-4o Model: {metadata['gpt4o_model']}")
        print(f"   📈 Success Rate: {metadata['total_concepts_developed']}/{len(analysis_modes)} modes")
        print(f"   🚀 Pipeline Version: {metadata['pipeline_version']}")
        
        # Test portfolio export
        print(f"\n📁 Exporting Concept Portfolio...")
        portfolio_export = await concept_pipeline.export_concept_portfolio(result)
        
        if portfolio_export['success']:
            portfolio = portfolio_export['portfolio']
            print("✅ Portfolio Export Successful!")
            print(f"   📄 Total Size: {portfolio_export['total_size']} characters")
            print(f"   🎨 Visual Concepts: {len(portfolio['visual_concepts'])}")
            print(f"   ⚙️  Technical Specs: {len(portfolio['technical_specifications'])}")
            print(f"   🎬 Creative Directions: {len(portfolio['creative_directions'])}")
            print(f"   📋 Implementation Guides: {len(portfolio['implementation_guides'])}")
            
            # Display recommended next steps
            next_steps = portfolio['execution_summary']['recommended_next_steps']
            print(f"\n📝 Recommended Next Steps:")
            for step in next_steps[:5]:  # Show first 5 steps
                print(f"   • {step}")
            if len(next_steps) > 5:
                print(f"   ... and {len(next_steps) - 5} more steps")
            
            # Display production estimate
            prod_estimate = portfolio['execution_summary']['estimated_production_time']
            print(f"\n⏱️  Production Estimate:")
            print(f"   📅 Time: {prod_estimate.get('estimated_time', 'Not available')}")
            print(f"   🎯 Efficiency: {prod_estimate.get('efficiency_note', 'Not available')}")
            
            # Save portfolio to file for reference
            portfolio_filename = f"8k_concept_portfolio_{brand_name.lower().replace(' ', '_')}.json"
            with open(portfolio_filename, 'w') as f:
                json.dump(portfolio, f, indent=2)
            print(f"\n💾 Portfolio saved to: {portfolio_filename}")
            
        else:
            print(f"❌ Portfolio export failed: {portfolio_export['error']}")
        
        print(f"\n🎯 Ready for 8K Production!")
        print("   All concepts, specifications, and guidance available")
        print("   No image generation required - pure conceptual development")
        print("   Professional satirical critique concepts ready for implementation")
        
    else:
        print(f"❌ Pure 8K concept pipeline failed: {result.error_message}")

async def test_single_concept_mode():
    """Test individual concept development modes."""
    
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    from integrations.pure_gpt4o_8k_client import PureGPT4o8KClient, Pure8KVisualRequest
    
    client = PureGPT4o8KClient(api_key=openai_api_key)
    
    print("\n🧪 Testing Individual Concept Development Modes")
    print("=" * 60)
    
    # Sample brand context for testing
    sample_brand_context = {
        'brand_name': 'Salesforce',
        'authenticity_score': 0.3,
        'satirical_vulnerabilities': [
            {'theme': 'AI washing', 'description': 'Overselling AI capabilities'},
            {'theme': 'Complexity masking', 'description': 'Making simple things complex'}
        ],
        'primary_positioning': 'Customer success platform'
    }
    
    sample_pentagram_prompt = "Corporate AI transparency contradiction expose through visual metaphor showing gap between promise and reality"
    
    # Test each mode individually
    test_modes = [
        ('8k_concept_development', '🎨'),
        ('technical_specifications', '⚙️'),
        ('creative_direction', '🎬'),
        ('implementation_guide', '📋')
    ]
    
    for mode, icon in test_modes:
        print(f"\n{icon} Testing {mode.replace('_', ' ').title()}")
        
        request = Pure8KVisualRequest(
            pentagram_prompt=sample_pentagram_prompt,
            brand_context=sample_brand_context,
            analysis_mode=mode,
            visual_style="professional_satirical_8k",
            resolution_target="8k_uhd"
        )
        
        result = await client.develop_8k_concept(request)
        
        if result.success:
            print(f"   ✅ Success - {result.concept_title}")
            print(f"   💡 Concept: {result.visual_concept[:100]}...")
            print(f"   ⏱️  Time: {result.processing_time:.2f}s")
            
            # Show mode-specific details
            if mode == '8k_concept_development' and result.alternative_concepts:
                print(f"   🔄 Alternatives: {len(result.alternative_concepts)}")
            elif mode == 'technical_specifications' and result.technical_specifications:
                print(f"   📐 Tech specs: {len(result.technical_specifications)} categories")
            elif mode == 'creative_direction' and result.creative_direction:
                print(f"   🎨 Creative guidance: {len(result.creative_direction)} sections")
            elif mode == 'implementation_guide' and result.implementation_steps:
                print(f"   📝 Implementation steps: {len(result.implementation_steps)}")
        else:
            print(f"   ❌ Failed: {result.error_message}")

if __name__ == "__main__":
    print("🚀 Pure GPT-4o 8K Concept Development Test Suite")
    print("=" * 60)
    
    # Run full pipeline test
    asyncio.run(test_pure_8k_concept_development())
    
    # Run individual mode tests
    asyncio.run(test_single_concept_mode())
    
    print("\n🎉 Test Suite Complete!")
    print("   Ready for production 8K satirical concept development")
