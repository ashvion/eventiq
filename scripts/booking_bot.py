import sys
import json
import asyncio
from playwright.async_api import async_playwright

async def run(event_name, user_name, user_email, seats):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            #Navigate to booking page
            print(f"DEBUG: Navigating to http://localhost:8000/booking/")
            await page.goto("http://localhost:8000/booking/", wait_until="networkidle")
            
            # Fill form
            await page.fill("input[name='name']", user_name)
            await page.fill("input[name='email']", user_email)
            
            # Select Event
            print(f"DEBUG: Looking for event '{event_name}'")
            # Wait for the select element itself first
            await page.wait_for_selector("select[name='event']", timeout=10000)
            
            # Find the option by text. We use state='attached' because options are not seen as 'visible' by Playwright.
            option_selector = f"select[name='event'] option:has-text('{event_name}')"
            try:
                await page.wait_for_selector(option_selector, state='attached', timeout=10000)
                event_value = await page.locator(option_selector).get_attribute("value")
                print(f"DEBUG: Found event value '{event_value}' for '{event_name}'. Selecting...")
                await page.select_option("select[name='event']", event_value)
            except Exception as e_opt:
                # Fallback: list all options to help debug
                opts = await page.eval_on_selector_all("select[name='event'] option", "els => els.map(el => el.textContent)")
                print(f"DEBUG: Could not find '{event_name}' in options: {opts}")
                raise e_opt

            # Select Seats
            print(f"DEBUG: Waiting for seats dropdown and selecting '{seats}'")
            await page.wait_for_selector("select[name='seats']", timeout=10000)
            
            # Ensure seats is a clean string representing an integer (e.g. '2')
            try:
                target_seats = str(int(float(seats)))
            except:
                target_seats = str(seats).strip()
                
            # Log all available options for seats to debug "did not find some options"
            seat_options_data = await page.eval_on_selector_all(
                "select[name='seats'] option", 
                "els => els.map(el => ({value: el.value, text: el.textContent.trim()}))"
            )
            print(f"DEBUG: Available seat options: {seat_options_data}")
            
            seat_values = [opt['value'] for opt in seat_options_data]
            
            if target_seats in seat_values:
                try:
                    await page.select_option("select[name='seats']", target_seats, timeout=5000)
                except:
                    print(f"DEBUG: Standard select_option failed for '{target_seats}'. Forcing via JS...")
                    await page.eval_on_selector("select[name='seats']", f"el => el.value = '{target_seats}'")
                    await page.locator("select[name='seats']").dispatch_event("change")
            else:
                # Try matching by text/label
                print(f"DEBUG: Value '{target_seats}' not found in values {seat_values}. Trying labels...")
                found_by_label = False
                for label_pattern in [target_seats, f"{target_seats} Seat", f"{target_seats} Seats"]:
                    for opt in seat_options_data:
                        if opt['text'] == label_pattern:
                            await page.eval_on_selector("select[name='seats']", f"el => el.value = '{opt['value']}'")
                            await page.locator("select[name='seats']").dispatch_event("change")
                            found_by_label = True
                            print(f"DEBUG: Selected by label '{label_pattern}'")
                            break
                    if found_by_label: break
                
                if not found_by_label:
                    print(f"DEBUG: Failed to find option for '{seats}'. Available labels: {[o['text'] for o in seat_options_data]}")
                    raise Exception(f"Seat option '{seats}' not found.")

            print("DEBUG: Seats selected.")
            
            # Enable console logging
            page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))

            # Submit
            print(f"Clicking submit button... Current URL: {page.url}")
            await page.click("button[type='submit']")
            print("Clicked submit.")
            
            # Wait for redirect to payment page
            try:
                print("Waiting for navigation to payment page...")
                await page.wait_for_url(lambda url: "/payment/" in url, timeout=30000)
                current_url = page.url
                print(f"Successfully reached payment page: {current_url}")
                print(json.dumps({"status": "success", "redirect_url": current_url}))
            except Exception as e_nav:
                # Capture current state for debugging
                current_url = page.url
                # CAPTURE SCREENSHOT ON FAILURE
                await page.screenshot(path="booking_failure.png")
                print("DEBUG: Captured booking_failure.png")
                
                try:
                    error_message = await page.locator(".alert-error").text_content()
                except:
                    error_message = "No error alert found"
                try:
                    overlay_display = await page.eval_on_selector("#processing-overlay", "el => el.style.display")
                except:
                    overlay_display = "Unknown"

                print(json.dumps({
                    "status": "error", 
                    "message": f"Navigation timeout. Current URL: {current_url}. Page Error: {error_message}. Overlay Display: {overlay_display}. Exception: {str(e_nav)}"
                }))
        except Exception as e_global:
            # BROAD FAILURE CAPTURE
            current_url = page.url
            await page.screenshot(path="booking_failure.png")
            print(f"DEBUG: captured booking_failure.png on global failure: {str(e_global)}")
            print(json.dumps({
                "status": "error",
                "message": f"Automation failed: {str(e_global)}. Current URL: {current_url}"
            }))
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(json.dumps({"status": "error", "message": "Missing arguments"}))
        sys.exit(1)
        
    event_name = sys.argv[1]
    name = sys.argv[2]
    email = sys.argv[3]
    seats = sys.argv[4]
    
    asyncio.run(run(event_name, name, email, seats))
