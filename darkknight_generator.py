#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DarkKnight Token 生成器
使用 Playwright 浏览器自动化生成有效的 x-zai-darkknight token
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from obfuscator import ObfuscatedStrings, TokenProtector

logger = logging.getLogger(__name__)


class DarkKnightGenerator:
    """DarkKnight Token 生成器"""
    
    def __init__(self, headless: bool = True):
        """
        初始化生成器
        
        Args:
            headless: 是否使用无头模式
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
        
    async def start(self):
        """启动浏览器"""
        try:
            self.playwright = await async_playwright().start()
            
            # 使用 Chromium 浏览器
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--window-size=1920,1080'
                ]
            )
            
            # 创建浏览器上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # 创建页面
            self.page = await self.context.new_page()
            
            logger.info("浏览器启动成功")
            
        except Exception as e:
            logger.error(f"启动浏览器失败: {str(e)}")
            raise
            
    async def close(self):
        """关闭浏览器"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器失败: {str(e)}")
            
    async def generate_darkknight(self, timeout: int = 30000) -> Optional[str]:
        """
        生成 DarkKnight Token
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            DarkKnight token 字符串
        """
        try:
            if not self.page:
                raise RuntimeError("浏览器未启动")
                
            # 读取 BLRNmSar.js 文件
            with open('BLRNmSar.js', 'r', encoding='utf-8') as f:
                darkknight_script = f.read()
                
            # 注入 DarkKnight 脚本
            await self.page.add_init_script(darkknight_script)
            
            # 访问 zai.is 首页以触发脚本初始化
            logger.info("访问 zai.is 首页...")
            await self.page.goto('https://zai.is', wait_until='networkidle', timeout=timeout)
            
            # 等待 DarkKnight 对象初始化
            logger.info("等待 DarkKnight 对象初始化...")
            await self.page.wait_for_function(
                'typeof window.DarkKnight !== "undefined" && window.DarkKnight.getToken',
                timeout=timeout
            )
            
            # 获取 DarkKnight token
            logger.info("获取 DarkKnight token...")
            darkknight_token = await self.page.evaluate('window.DarkKnight.getToken()')
            
            if not darkknight_token:
                raise RuntimeError("未能获取 DarkKnight token")
                
            logger.info(f"成功获取 DarkKnight token: {TokenProtector.mask_token(darkknight_token, show_chars=20)}")
            
            return darkknight_token
            
        except Exception as e:
            logger.error(f"生成 DarkKnight token 失败: {str(e)}")
            return None
            
    async def get_darkknight_with_retry(self, max_retries: int = 3, timeout: int = 30000) -> Optional[str]:
        """
        带重试的 DarkKnight token 获取
        
        Args:
            max_retries: 最大重试次数
            timeout: 超时时间（毫秒）
            
        Returns:
            DarkKnight token 字符串
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"尝试获取 DarkKnight token (第 {attempt + 1}/{max_retries} 次)...")
                
                token = await self.generate_darkknight(timeout)
                
                if token:
                    return token
                    
                logger.warning(f"第 {attempt + 1} 次尝试失败，token 为空")
                
            except Exception as e:
                logger.error(f"第 {attempt + 1} 次尝试失败: {str(e)}")
                
            # 如果不是最后一次尝试，重启浏览器
            if attempt < max_retries - 1:
                logger.info("重启浏览器...")
                await self.close()
                await asyncio.sleep(2)  # 等待 2 秒
                await self.start()
                
        logger.error(f"经过 {max_retries} 次尝试后仍无法获取 DarkKnight token")
        return None


async def generate_darkknight_token(headless: bool = True, max_retries: int = 3) -> Optional[str]:
    """
    生成 DarkKnight Token 的便捷函数
    
    Args:
        headless: 是否使用无头模式
        max_retries: 最大重试次数
        
    Returns:
        DarkKnight token 字符串
    """
    async with DarkKnightGenerator(headless=headless) as generator:
        return await generator.get_darkknight_with_retry(max_retries=max_retries)


def generate_darkknight_sync(headless: bool = True, max_retries: int = 3) -> Optional[str]:
    """
    同步版本的 DarkKnight Token 生成函数
    
    Args:
        headless: 是否使用无头模式
        max_retries: 最大重试次数
        
    Returns:
        DarkKnight token 字符串
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    return loop.run_until_complete(generate_darkknight_token(headless, max_retries))


if __name__ == '__main__':
    # 测试代码
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("开始生成 DarkKnight token...")
    token = generate_darkknight_sync(headless=False, max_retries=3)
    
    if token:
        print(f"\n成功获取 DarkKnight token:")
        print(f"{token}\n")
        sys.exit(0)
    else:
        print("\n失败: 无法获取 DarkKnight token\n")
        sys.exit(1)