import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.goofish.com/")
        print("请在浏览器完成登录，回到终端按 Enter 保存登录态...")
        await asyncio.get_running_loop().run_in_executor(None, input)
        await context.storage_state(path="storage_state.json")
        await browser.close()
        print("已保存: storage_state.json")

if __name__ == "__main__":
    asyncio.run(main())
