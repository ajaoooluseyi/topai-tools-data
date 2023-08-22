from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd


def scrape_tool_details(driver, tool_url):
    # Load the individual tool's page
    driver.get(tool_url)
    
    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[1])

    # Wait for the page to load (you may need to adjust the wait time depending on the website)
    driver.implicitly_wait(10)

    # Find and extract the use case information from the tool's page
    use_case_items = driver.find_elements(By.XPATH, '//div[@class="my-4"]//ol//li')
    if use_case_items:
        use_cases = [item.text.strip() for item in use_case_items]
        use_cases = ', '.join(use_cases)
    else:
        use_cases = 'N/A'  # If use cases are not found, use 'N/A' to indicate missing data
    
    # Close the current tab and switch back to the main content
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return use_cases


def scrape_tools_data(url):
    # Set up Chrome WebDriver
    options = Options()
    options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
    driver = webdriver.Chrome(options=options)

    # Navigate to the website
    driver.get(url)

    # Wait for the page to load (you may need to adjust the wait time depending on the website)
    driver.implicitly_wait(10)

    tools_data = []

    # Find all the tool entries on the page
    tools = driver.find_elements(By.CLASS_NAME, "tool_box")
    print(tools)
    for tool in tools:
        try:
            # Extract the required information for each tool
            tool_name = tool.find_element(By.XPATH, './/h5//a').text.strip()
            # tool_url = tool.find_element(By.XPATH, './/a[contains(@class, "rounded")]').get_attribute('href')
            tool_description = tool.find_element(By.XPATH, './/p[contains(@class, "font-weight-lighter")]').text.strip()
            tool_pricing = tool.find_element(By.XPATH, './/span[contains(@class, "pricing-badge")]').text.strip()
            tool_tags = [tag.text.strip() for tag in tool.find_elements(By.XPATH, './/span[contains(@class, "badge")]')]

            try:
                # Get the use case for each tool by visiting the individual tool's page
                tool_url = WebDriverWait(tool, 10).until(EC.presence_of_element_located((By.XPATH, './/a[contains(@class, "rounded")]'))).get_attribute('href')
                tool_use_case = scrape_tool_details(driver, tool_url)
            except Exception as e:
                print(f"Error scraping use case for '{tool_name}': {e}")
                tool_use_case = 'N/A'  # In case of an error, use 'N/A' to indicate missing data
            
            print(f"Scraped data for '{tool_name}")
            # Store the extracpyted data in a dictionary
            tool_data = {
                'Tool Name': tool_name,
                'Tool URL': tool_url,
                'What is': tool_description,
                'Pricing': tool_pricing,
                'Tags': ', '.join(tool_tags),
                'Tool possible use cases': tool_use_case
            }

            tools_data.append(tool_data)

        except Exception as e:
            print(f"Error processing tool entry: {e}")

    # Close the browser after scraping
    driver.quit()

    return tools_data




def save_to_excel(tools_data, output_file):
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(tools_data)

    # Save the DataFrame to an Excel file
    df.to_excel(output_file, index=False)


if __name__ == '__main__':
    # URL of the website to scrape
    url = 'https://topai.tools/browse'

    # Scrape the data from the website using Selenium
    tools_data = scrape_tools_data(url)

    # Save the data to an Excel file
    output_file = 'tools_data.xlsx'
    save_to_excel(tools_data, output_file)

    print(f"Data has been scraped and saved to '{output_file}' in Excel format.")
