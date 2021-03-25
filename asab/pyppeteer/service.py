import asyncio
import logging
import os

import pyppeteer
import urllib.parse
import asab

#

L = logging.getLogger(__name__)

#


class PyppeteerService(asab.Service):

	"""
	Navigates to a page, takes a screenshot and saves it to a file.
	"""

	# PDF settings: https://github.com/puppeteer/puppeteer/blob/main/docs/api.md#pagepdfoptions
	# https://github.com/miyakogi/pyppeteer#usage

	def __init__(self, app, service_name="asab.PyppeteerService"):
		super().__init__(app, service_name)

		self.Containers = {}
		self.App = app
		self.Loop = app.Loop
		self.SavePath = asab.Config.get("general", "var_dir")

	async def capture_screenshot(self, url, file_name=None):
		SUFFIX = ".png"
		if file_name is None:
			url_parsed = urllib.parse.urlparse(url)
			file_name = "{}-{}".format(url_parsed.netloc, url_parsed.path.replace("/", "-"))
		if not file_name.endswith(SUFFIX):
			file_name = "{}{}".format(file_name, SUFFIX)
		save_path = os.path.join(self.SavePath, file_name)
		browser = await pyppeteer.launch()
		page = await browser.newPage()
		await page.goto(
			url,
			{
				'waitUntil': 'networkidle0'
				# No need of retrieving a message from UI to BE that page is fully loaded
			}
		)

		# Screenshot
		await page.screenshot({
			'fullPage': True,
			'path': save_path
		})

		await browser.close()
		L.log(asab.LOG_NOTICE, "Screenshot saved to {}".format(save_path), struct_data={"source_url": url})
		return True

	async def capture_pdf(self, url, file_name=None):
		raise NotImplementedError()
		if file_name is None:
			url_parsed = urllib.parse.urlparse(url)
			file_name = "{}-{}".format(url_parsed.netloc, url_parsed.path.replace("/", "-"))
		save_path = os.path.join(self.SavePath, file_name)
		browser = await pyppeteer.launch()
		page = await browser.newPage()
		await page.goto(
			url,
			{
				'waitUntil': 'networkidle0'
				# No need of retrieving a message from UI to BE that page is fully loaded
			}
		)
		# PDF
		await page.pdf({
			'format': 'A4',
			'preferCSSPageSize': True,
			'landscape': True,
			'scale': 1,  # Sets a scale of the pdf ((0.1-2))
			'printBackground': True,  # Print background styles
			'path': save_path})

		await browser.close()
		print("Files has been generated")
		return
