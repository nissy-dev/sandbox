import { test, expect } from "../vrt/utils";
import { App } from "./App";

test.use({ viewport: { width: 500, height: 500 } });

test("should work", async ({ mount, page }) => {
  await page.evaluate(() => {
    // @ts-ignore
    window.__globalData__ = "global data";
  });

  const component = await mount(<App />);
  await expect(component).toContainText("Hello World!");
  await page.screenshot({ path: "screenshot.png" });
});
