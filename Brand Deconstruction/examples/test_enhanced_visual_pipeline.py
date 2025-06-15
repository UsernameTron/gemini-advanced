# File: examples/test_enhanced_visual_pipeline.py

import asyncio
import os
import sys
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.enhanced_visual_pipeline import EnhancedVisualPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_gpt4o_enhanced_pipeline():
    """Test the GPT-4o enhanced visual pipeline."""
    
    # Get OpenAI API key
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   Example: export OPENAI_API_KEY=your_api_key_here")
        return
    
    # Create enhanced pipeline
    try:
        enhanced_pipeline = EnhancedVisualPipeline(
            deconstruction_workflow=None,  # Using mock for now
            openai_api_key=openai_api_key,
            enable_sora=True
        )
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {str(e)}")
        return
    
    # Test with target URL
    test_url = "https://salesforce.com"
    
    print(f"🎯 Testing GPT-4o Enhanced Visual Pipeline with: {test_url}")
    print("🧠 Using GPT-4o for sophisticated visual concept development")
    print("🎬 Preparing for Sora video generation (when available)")
    print("=" * 70)
    
    try:
        result = await enhanced_pipeline.execute_enhanced_pipeline(
            url=test_url,
            visual_approaches=['satirical_visual_analysis', 'sora_storyboard', 'composite_design'],
            include_video=True
        )
        
        if result.success:
            print(f"\n✅ Enhanced pipeline completed successfully!")
            print(f"📊 Brand Analysis: {result.brand_deconstruction['brand_analysis']['brand_name']}")
            print(f"🎯 Authenticity Score: {result.brand_deconstruction['brand_analysis']['authenticity_score']:.2f}")
            print(f"🧠 GPT-4o Concepts Generated: {len(result.gpt4o_concepts)}")
            
            # Display concept details
            for i, concept in enumerate(result.gpt4o_concepts):
                if concept.success:
                    print(f"\n🎨 Concept {i+1}: {concept.satirical_approach}")
                    print(f"   💡 Core Visual: {concept.visual_concept[:100] if concept.visual_concept else 'N/A'}...")
                    if concept.sora_storyboard:
                        print(f"   🎬 Storyboard: {len(concept.sora_storyboard)} scenes ready for Sora")
                    if concept.technical_specs:
                        print(f"   ⚙️  Technical specs provided for implementation")
                    print(f"   ⏱️  Processing time: {concept.processing_time:.2f}s")
                else:
                    print(f"   ❌ Concept {i+1}: {concept.error_message}")
            
            if result.sora_videos:
                print(f"\n🎬 Sora Videos: {len(result.sora_videos)} video concepts")
                for i, video in enumerate(result.sora_videos):
                    if video.success:
                        print(f"   ✅ Video {i+1}: Ready for generation")
                    else:
                        print(f"   📋 Video {i+1}: {video.error_message}")
            
            print(f"\n⏱️  Total time: {result.total_processing_time:.2f}s")
            print(f"🚀 Pipeline version: {result.pipeline_metadata['pipeline_version']}")
            
            # Show detailed visual concept if available
            if result.gpt4o_concepts and result.gpt4o_concepts[0].success:
                first_concept = result.gpt4o_concepts[0]
                if first_concept.detailed_instructions:
                    print(f"\n📝 Sample Visual Concept Detail:")
                    print(f"   {first_concept.detailed_instructions[:200]}...")
            
        else:
            print(f"❌ Enhanced pipeline failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Pipeline execution error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_multiple_approaches():
    """Test different visual approaches separately"""
    
    print(f"\n🔬 Testing Individual Visual Approaches")
    print("=" * 50)
    
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ OpenAI API key required for individual approach testing")
        return
    
    enhanced_pipeline = EnhancedVisualPipeline(
        openai_api_key=openai_api_key,
        enable_sora=True
    )
    
    approaches = ['satirical_visual_analysis', 'composite_design', 'sora_storyboard']
    test_url = "https://apple.com"
    
    for approach in approaches:
        print(f"\n🎨 Testing approach: {approach}")
        try:
            result = await enhanced_pipeline.execute_enhanced_pipeline(
                url=test_url,
                visual_approaches=[approach],
                include_video=(approach == 'sora_storyboard')
            )
            
            if result.success and result.gpt4o_concepts:
                concept = result.gpt4o_concepts[0]
                print(f"   ✅ Success: {concept.satirical_approach}")
                print(f"   ⏱️  Time: {concept.processing_time:.2f}s")
            else:
                print(f"   ❌ Failed: {result.error_message}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🎯 Brand Deconstruction Engine - GPT-4o Enhanced Visual Pipeline Test")
    print("=" * 70)
    
    # Run main test
    asyncio.run(test_gpt4o_enhanced_pipeline())
    
    # Run individual approach tests
    asyncio.run(test_multiple_approaches())
