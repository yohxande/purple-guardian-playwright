"""
💜 Basic example of Purple Guardian usage
"""

import asyncio
from purple_guardian import PurpleGuardian, BasicWorkflow, PurpleConfig


async def main():
    """Basic Purple Guardian example"""
    
    # Create configuration
    config = PurpleConfig(
        headless=False,  # Show browser for demo
        max_retries=2,
        screenshot_on_violation=True
    )
    
    # Create workflow
    workflow = BasicWorkflow(
        url="https://example.com",
        actions=[
            {"type": "wait", "timeout": 2000},
            {"type": "screenshot", "path": "example_page.png"}
        ]
    )
    
    # Run with Purple Guardian
    async with PurpleGuardian(config=config) as guardian:
        print("💜 Running basic Purple Guardian example...")
        
        try:
            result = await guardian.run(workflow)
            print(f"✨ Success! Result: {result}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Show statistics
        stats = guardian.get_stats()
        print(f"📊 Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())