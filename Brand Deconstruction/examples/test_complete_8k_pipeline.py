# File: examples/test_complete_8k_pipeline.py

import asyncio
import os
import json
import sys
from pathlib import Path

# Add the parent directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from integrations.complete_8k_visual_pipeline import Complete8KVisualPipeline
from workflows.brand_deconstruction import CompleteBrandDeconstructionWorkflow

async def test_complete_8k_visual_pipeline():
    """Test the complete GPT-4o + gpt-image-1 8K visual pipeline."""
    
    # Initialize workflow
    deconstruction_workflow = CompleteBrandDeconstructionWorkflow()
    
    # Get OpenAI API key
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    # Create complete 8K pipeline
    complete_pipeline = Complete8KVisualPipeline(
        deconstruction_workflow=deconstruction_workflow,
        openai_api_key=openai_api_key
    )
    
    # Test with target URL
    test_url = "https://salesforce.com"
    
    print("🚀 Complete 8K Visual Pipeline Test")
    print("=" * 60)
    print(f"🎯 Target: {test_url}")
    print("🧠 Phase 1: Brand Deconstruction")
    print("💡 Phase 2: GPT-4o Concept Development")
    print("🖼️  Phase 3: gpt-image-1 High-Quality Generation")
    print("")
    
    # Configure image generation
    image_config = {
        'size': '1536x1024',  # High resolution landscape
        'quality': 'high',
        'output_format': 'png',
        'output_compression': 95,
        'background': 'auto'
    }
    
    result = await complete_pipeline.execute_complete_pipeline(
        url=test_url,
        concept_modes=['8k_concept_development', 'technical_specifications', 'creative_direction'],
        generate_variations=True,
        image_config=image_config
    )
    
    if result.success:
        print("✅ Complete 8K Visual Pipeline Successful!")
        print("=" * 60)
        
        # Display brand analysis
        brand_name = result.brand_deconstruction.brand_analysis.brand_name
        auth_score = result.brand_deconstruction.brand_analysis.authenticity_score
        vulnerabilities = result.brand_deconstruction.brand_analysis.satirical_vulnerabilities
        
        print(f"📊 Brand Analysis:")
        print(f"   🏢 Brand: {brand_name}")
        print(f"   🎯 Authenticity Score: {auth_score:.2f}")
        print(f"   🔍 Vulnerabilities Found: {len(vulnerabilities)}")
        
        # Display concept development results
        if result.concept_development and result.concept_development['success']:
            concepts = result.concept_development['concepts']
            print(f"\n💡 Concept Development:")
            print(f"   🧠 Concepts Created: {len(concepts)}")
            print(f"   ⏱️  Development Time: {result.concept_development['processing_time']:.2f}s")
            
            for i, concept in enumerate(concepts):
                if concept.success:
                    print(f"\n   🎨 Concept {i+1}: {concept.concept_title}")
                    print(f"      💭 Core Visual: {concept.visual_concept[:100]}...")
                    if concept.alternative_concepts:
                        print(f"      🔄 Variations: {len(concept.alternative_concepts)}")
                    if concept.technical_specifications:
                        print(f"      ⚙️  Technical specs provided")
        
        # Display image generation results
        print(f"\n🖼️  Image Generation:")
        print(f"   🎨 Images Generated: {len(result.generated_images)}")
        print(f"   ✅ Successful: {result.pipeline_metadata['successful_generations']}")
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
            else:
                print(f"   ❌ Image {i+1}: {image.error_message}")
        
        # Display pipeline performance
        metadata = result.pipeline_metadata
        print(f"\n📊 Pipeline Performance:")
        print(f"   ⏱️  Total Time: {metadata['total_processing_time']:.2f}s")
        print(f"   🧠 GPT-4o Time: {metadata['concept_development_time']:.2f}s")
        print(f"   🖼️  gpt-image-1 Time: {metadata['image_generation_time']:.2f}s")
        print(f"   🚀 Pipeline Version: {metadata['pipeline_version']}")
        print(f"   🔧 Models Used: {metadata['gpt4o_model']} + {metadata['image_model']}")
        
        # Save images to files
        print(f"\n💾 Saving Generated Images...")
        save_result = await complete_pipeline.save_generated_images(result, "output/satirical_images")
        
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
        
        # Create portfolio summary
        print(f"\n📋 Creating Portfolio Summary...")
        portfolio_summary = {
            'brand_analysis': {
                'brand_name': brand_name,
                'authenticity_score': auth_score,
                'satirical_vulnerabilities': [v.get('theme', '') for v in vulnerabilities]
            },
            'visual_concepts': [
                {
                    'title': concept.concept_title,
                    'visual_concept': concept.visual_concept,
                    'alternatives': len(concept.alternative_concepts) if concept.alternative_concepts else 0
                }
                for concept in result.concept_development['concepts'] if concept.success
            ],
            'generated_images': [
                {
                    'image_id': i+1,
                    'specs': image.image_specs,
                    'generation_time': image.processing_time
                }
                for i, image in enumerate(result.generated_images) if image.success
            ],
            'pipeline_performance': metadata,
            'saved_files': save_result['saved_files'] if save_result['success'] else []
        }
        
        # Save portfolio summary
        portfolio_filename = f"8k_visual_portfolio_{brand_name.lower().replace(' ', '_')}.json"
        with open(portfolio_filename, 'w') as f:
            json.dump(portfolio_summary, f, indent=2)
        
        print(f"📋 Portfolio summary saved to: {portfolio_filename}")
        
        print(f"\n🎉 Complete 8K Visual Pipeline Test Successful!")
        print("   ✅ Brand analyzed and deconstructed")
        print("   ✅ Sophisticated concepts developed with GPT-4o")
        print("   ✅ High-quality images generated with gpt-image-1")
        print("   ✅ All files saved and documented")
        print("   🚀 Ready for professional satirical content production!")
        
    else:
        print(f"❌ Complete pipeline failed: {result.error_message}")

async def test_image_quality_variations():
    """Test different image quality and format options."""
    
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    from integrations.gpt_image_1_client import GPTImage1Client, GPTImage1Request
    
    client = GPTImage1Client(api_key=openai_api_key)
    
    print("\n🧪 Testing Image Quality Variations")
    print("=" * 60)
    
    # Sample concept for testing
    sample_prompt = "Professional corporate photography showing a modern office building with oversized 'AI POWERED' signs, but the building is visibly cracking and unstable, employees running out in panic, dramatic contrast between promise and reality, high-resolution, studio lighting, satirical irony"
    
    # Test different configurations
    test_configs = [
        {
            'name': '8K Ultra High Quality',
            'config': {
                'size': '1536x1024',
                'quality': 'high',
                'output_format': 'png',
                'output_compression': 100
            }
        },
        {
            'name': 'Web Optimized',
            'config': {
                'size': '1024x1024',
                'quality': 'medium',
                'output_format': 'jpeg',
                'output_compression': 85
            }
        },
        {
            'name': 'Print Ready',
            'config': {
                'size': '1536x1024',
                'quality': 'high',
                'output_format': 'png',
                'output_compression': 95
            }
        }
    ]
    
    for i, test_config in enumerate(test_configs):
        print(f"\n🎨 Testing {test_config['name']}...")
        
        request = GPTImage1Request(
            optimized_prompt=sample_prompt,
            brand_context={'brand_name': 'Test Corp', 'authenticity_score': 0.3},
            technical_specifications={'intended_use': 'professional'},
            generation_config=test_config['config']
        )
        
        result = await client.generate_satirical_image(request)
        
        if result.success:
            specs = result.image_specs
            print(f"   ✅ Success!")
            print(f"   📐 Size: {specs.get('size')}")
            print(f"   🎨 Format: {specs.get('format')}")
            print(f"   📊 Quality: {specs.get('quality')}")
            print(f"   💾 File Size: {specs.get('file_size_estimate', 0) // 1024:.1f}KB")
            print(f"   ⏱️  Time: {result.processing_time:.2f}s")
        else:
            print(f"   ❌ Failed: {result.error_message}")

if __name__ == "__main__":
    print("🚀 Complete 8K Visual Pipeline Test Suite")
    print("   GPT-4o Concept Development + gpt-image-1 Generation")
    print("=" * 60)
    
    # Run complete pipeline test
    asyncio.run(test_complete_8k_visual_pipeline())
    
    # Run quality variations test
    asyncio.run(test_image_quality_variations())
    
    print("\n🎉 All Tests Complete!")
    print("   Ready for production 8K satirical content generation")
