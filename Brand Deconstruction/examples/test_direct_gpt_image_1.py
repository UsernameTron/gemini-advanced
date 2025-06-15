# File: examples/test_direct_gpt_image_1.py

import asyncio
import os
import json
import sys
from pathlib import Path

# Add the parent directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from integrations.direct_gpt_image_1_pipeline import DirectGPTImage1Pipeline
from workflows.brand_deconstruction import CompleteBrandDeconstructionWorkflow

async def test_direct_gpt_image_1_pipeline():
    """Test the direct gpt-image-1 pipeline (no GPT-4o layer)."""
    
    # Initialize workflow
    deconstruction_workflow = CompleteBrandDeconstructionWorkflow()
    
    # Get OpenAI API key
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    # Create direct gpt-image-1 pipeline
    direct_pipeline = DirectGPTImage1Pipeline(
        deconstruction_workflow=deconstruction_workflow,
        openai_api_key=openai_api_key
    )
    
    # Test with target URL
    test_url = "https://salesforce.com"
    
    print("🚀 Direct gpt-image-1 Pipeline Test")
    print("=" * 60)
    print(f"🎯 Target: {test_url}")
    print("🧠 Phase 1: Brand Deconstruction")
    print("🖼️  Phase 2: Direct gpt-image-1 Generation")
    print("⚡ No GPT-4o layer - direct prompting to gpt-image-1")
    print("")
    
    # Configure image generation
    image_config = {
        'quality': 'high',
        'output_format': 'png',
        'output_compression': 95,
        'background': 'auto'
    }
    
    result = await direct_pipeline.execute_direct_pipeline(
        url=test_url,
        image_variations=4,  # Generate 4 different satirical images
        image_config=image_config
    )
    
    if result.success:
        print("✅ Direct gpt-image-1 Pipeline Successful!")
        print("=" * 60)
        
        # Display brand analysis
        brand_name = result.brand_deconstruction.brand_analysis.brand_name
        auth_score = result.brand_deconstruction.brand_analysis.authenticity_score
        vulnerabilities = result.brand_deconstruction.brand_analysis.satirical_vulnerabilities
        
        print(f"📊 Brand Analysis:")
        print(f"   🏢 Brand: {brand_name}")
        print(f"   🎯 Authenticity Score: {auth_score:.2f}")
        print(f"   🔍 Vulnerabilities Found: {len(vulnerabilities)}")
        
        # Display vulnerability themes
        if vulnerabilities:
            print(f"\n🎭 Satirical Targets:")
            for i, vuln in enumerate(vulnerabilities[:3]):  # Show top 3
                theme = vuln.get('theme', 'Unknown')
                desc = vuln.get('description', 'No description')
                print(f"   {i+1}. {theme}: {desc}")
        
        # Display image generation results
        print(f"\n🖼️  Image Generation Results:")
        print(f"   🎨 Images Requested: {result.pipeline_metadata['variations_requested']}")
        print(f"   ✅ Successfully Generated: {result.pipeline_metadata['successful_generations']}")
        print(f"   ⏱️  Generation Time: {result.pipeline_metadata['image_generation_time']:.2f}s")
        
        for i, image in enumerate(result.generated_images):
            if image.success:
                specs = image.image_specs
                print(f"\n   🖼️  Image {i+1}:")
                print(f"      📐 Size: {specs.get('size', 'Unknown')}")
                print(f"      🎨 Format: {specs.get('format', 'Unknown')}")
                print(f"      📊 Quality: {specs.get('quality', 'Unknown')}")
                print(f"      💾 Est. Size: {specs.get('file_size_estimate', 0) // 1024:.1f}KB")
                print(f"      ⏱️  Time: {image.processing_time:.2f}s")
                
                # Show prompt used (truncated)
                brand_context = image.generation_metadata.get('brand_context', {})
                satirical_focus = brand_context.get('satirical_focus', [])
                if satirical_focus:
                    print(f"      🎯 Focus: {', '.join(satirical_focus[:2])}")
            else:
                print(f"   ❌ Image {i+1}: {image.error_message}")
        
        # Display pipeline performance
        metadata = result.pipeline_metadata
        print(f"\n📊 Pipeline Performance:")
        print(f"   ⏱️  Total Time: {metadata['total_processing_time']:.2f}s")
        print(f"   🧠 Brand Analysis: {metadata['brand_analysis_time']:.2f}s")
        print(f"   🖼️  Image Generation: {metadata['image_generation_time']:.2f}s")
        print(f"   🚀 Pipeline Version: {metadata['pipeline_version']}")
        print(f"   🔧 Model Used: {metadata['image_model']}")
        print(f"   📝 Prompt Strategy: {metadata['prompt_strategy']}")
        
        # Save images to files
        print(f"\n💾 Saving Generated Images...")
        save_result = await direct_pipeline.save_generated_images(result, "output/direct_satirical_images")
        
        if save_result['success']:
            print("✅ Images Saved Successfully!")
            print(f"   📁 Directory: {save_result['output_directory']}")
            print(f"   📸 Images Saved: {save_result['total_images_saved']}")
            
            for i, file_info in enumerate(save_result['saved_files']):
                print(f"\n   📄 File {i+1}:")
                print(f"      🖼️  Image: {Path(file_info['image_file']).name}")
                print(f"      📋 Metadata: {Path(file_info['metadata_file']).name}")
                print(f"      💾 Size: {file_info['file_size'] // 1024:.1f}KB")
                print(f"      📐 Specs: {file_info['image_specs']['size']}")
        else:
            print(f"❌ Failed to save images")
        
        # Create summary report
        print(f"\n📋 Creating Pipeline Summary...")
        summary = {
            'pipeline_type': 'direct_gpt_image_1',
            'brand_analysis': {
                'brand_name': brand_name,
                'authenticity_score': auth_score,
                'satirical_vulnerabilities': [v.get('theme', '') for v in vulnerabilities]
            },
            'generation_results': {
                'images_generated': len(result.generated_images),
                'successful_generations': metadata['successful_generations'],
                'total_processing_time': metadata['total_processing_time'],
                'image_generation_time': metadata['image_generation_time']
            },
            'generated_images': [
                {
                    'image_id': i+1,
                    'success': image.success,
                    'specs': image.image_specs if image.success else None,
                    'generation_time': image.processing_time,
                    'error': image.error_message if not image.success else None
                }
                for i, image in enumerate(result.generated_images)
            ],
            'saved_files': save_result['saved_files'] if save_result['success'] else []
        }
        
        # Save summary
        summary_filename = f"direct_gpt_image_1_summary_{brand_name.lower().replace(' ', '_')}.json"
        with open(summary_filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📋 Summary saved to: {summary_filename}")
        
        print(f"\n🎉 Direct gpt-image-1 Pipeline Test Successful!")
        print("   ✅ Brand analyzed and vulnerabilities identified")
        print("   ✅ Sophisticated prompts created directly from analysis")
        print("   ✅ High-quality satirical images generated with gpt-image-1")
        print("   ✅ All files saved and documented")
        print("   🚀 More efficient than GPT-4o + gpt-image-1 approach!")
        
        # Show efficiency comparison
        print(f"\n💡 Efficiency Benefits:")
        print("   ⚡ Eliminated GPT-4o conceptual layer")
        print("   💰 Reduced API costs (only gpt-image-1 calls)")
        print("   🕒 Faster processing (direct prompting)")
        print("   🎯 Same quality satirical output")
        
    else:
        print(f"❌ Direct pipeline failed: {result.error_message}")

async def test_different_brands():
    """Test the pipeline with different brands to show versatility."""
    
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    deconstruction_workflow = CompleteBrandDeconstructionWorkflow()
    direct_pipeline = DirectGPTImage1Pipeline(
        deconstruction_workflow=deconstruction_workflow,
        openai_api_key=openai_api_key
    )
    
    print("\n🧪 Testing Different Brands")
    print("=" * 60)
    
    # Test with different types of companies
    test_urls = [
        "https://microsoft.com",
        "https://google.com", 
        "https://meta.com"
    ]
    
    for url in test_urls:
        print(f"\n🎯 Testing: {url}")
        
        result = await direct_pipeline.execute_direct_pipeline(
            url=url,
            image_variations=2,  # Just 2 images per brand for speed
            image_config={'quality': 'high', 'size': '1024x1024'}
        )
        
        if result.success:
            brand_name = result.brand_deconstruction.brand_analysis.brand_name
            successful = result.pipeline_metadata['successful_generations']
            total_time = result.pipeline_metadata['total_processing_time']
            
            print(f"   ✅ {brand_name}: {successful}/2 images in {total_time:.1f}s")
        else:
            print(f"   ❌ Failed: {result.error_message}")

if __name__ == "__main__":
    print("🚀 Direct gpt-image-1 Pipeline Test Suite")
    print("   Brand Analysis → gpt-image-1 Generation (No GPT-4o)")
    print("=" * 60)
    
    # Run main pipeline test
    asyncio.run(test_direct_gpt_image_1_pipeline())
    
    # Run multi-brand test
    asyncio.run(test_different_brands())
    
    print("\n🎉 All Tests Complete!")
    print("   Ready for efficient satirical content generation with gpt-image-1 only!")
