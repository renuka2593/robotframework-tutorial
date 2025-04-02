"""
Products Page Object for SauceDemo tests.
"""
from robot.api.deco import keyword
from resources.pages.saucedemo.BasePage import BasePage


class ProductsPage(BasePage):
    """
    Page Object for SauceDemo products page.
    Handles products page functionality and verification.
    """

    def __init__(self):
        """Initialize the products page object."""
        super().__init__()
        
        # Define selectors
        self.selectors = {
            'inventory_container': 'css=.inventory_container',
            'inventory_list': 'css=.inventory_list',
            'inventory_items': 'css=.inventory_item',
            'inventory_item_name': 'css=.inventory_item_name',
            'inventory_item_price': 'css=.inventory_item_price',
            'add_to_cart_button': 'css=button[data-test^="add-to-cart"]',
            'remove_button': 'css=button[data-test^="remove"]',
            'shopping_cart': 'css=.shopping_cart_link',
            'shopping_cart_badge': 'css=.shopping_cart_badge',
            'product_sort_container': 'css=.product_sort_container',
            'burger_menu': 'id=react-burger-menu-btn',
            'logout_link': 'id=logout_sidebar_link',
            'page_title': 'css=.title',
            'header_container': 'css=.header_container',
            'specific_product': 'css=.inventory_item:has-text("{product_name}")',
            'product_add_button': 'css=.inventory_item:has-text("{product_name}") button',
            'footer': 'css=.footer'
        }

    @keyword
    def verify_products_page_loaded(self):
        """
        Verify that the products page is loaded properly.
        
        Returns:
            bool: True if the page is loaded
        """
        # Verify key elements are visible
        self.element_should_be_visible(self.selectors['inventory_container'])
        self.element_should_be_visible(self.selectors['inventory_list'])
        
        # Verify page title
        self.verify_page_title("Swag Labs")
        
        # Verify products page header
        self.element_should_contain_text(self.selectors['page_title'], "Products")
        
        self.logger.info("Products page loaded successfully")
        return True

    @keyword
    def get_product_count(self):
        """
        Get the number of products displayed on the page.
        
        Returns:
            int: Number of products
        """
        browser = self._get_browser_library()
        count = browser.get_element_count(self.selectors['inventory_items'])
        self.logger.info(f"Found {count} products on the page")
        return count

    @keyword
    def sort_products(self, sort_option):
        """
        Sort the products using the specified sort option.
        
        Args:
            sort_option (str): Sort option (e.g., "az", "za", "lohi", "hilo")
        """
        browser = self._get_browser_library()
        
        # Click on the sort dropdown
        browser.click(self.selectors['product_sort_container'])
        
        # Map friendly names to option values
        option_map = {
            "az": "az",
            "za": "za", 
            "lohi": "lohi",
            "hilo": "hilo",
            "name_asc": "az",
            "name_desc": "za",
            "price_asc": "lohi", 
            "price_desc": "hilo"
        }
        
        # Get the actual option value
        option_value = option_map.get(sort_option.lower(), sort_option)
        
        # Select the option
        selector = f'css=option[value="{option_value}"]'
        browser.click(selector)
        self.logger.info(f"Sorted products using option: {sort_option}")

    @keyword
    def add_product_to_cart(self, product_name):
        """
        Add a specific product to the cart.
        
        Args:
            product_name (str): Name of the product to add
        """
        browser = self._get_browser_library()
        
        # Generate the selector for the product's add button
        product_selector = self.selectors['specific_product'].format(product_name=product_name)
        button_selector = self.selectors['product_add_button'].format(product_name=product_name)
        
        # Make sure the product exists
        self.element_should_be_visible(product_selector)
        
        # Click the add to cart button
        browser.click(button_selector)
        self.logger.info(f"Added product to cart: {product_name}")

    @keyword
    def remove_product_from_cart(self, product_name):
        """
        Remove a specific product from the cart.
        
        Args:
            product_name (str): Name of the product to remove
        """
        browser = self._get_browser_library()
        
        # Generate the selector for the product's remove button
        product_selector = self.selectors['specific_product'].format(product_name=product_name)
        # For remove button, we need to adjust the selector because button text has changed
        button_selector = f'css=.inventory_item:has-text("{product_name}") button[data-test^="remove"]'
        
        # Make sure the product exists
        self.element_should_be_visible(product_selector)
        
        # Click the remove button
        browser.click(button_selector)
        self.logger.info(f"Removed product from cart: {product_name}")

    @keyword
    def get_cart_count(self):
        """
        Get the number of items in the cart.
        
        Returns:
            int: Number of items in the cart, 0 if cart is empty
        """
        browser = self._get_browser_library()
        
        # Check if cart badge exists
        if browser.get_element_count(self.selectors['shopping_cart_badge']) > 0:
            badge_text = browser.get_text(self.selectors['shopping_cart_badge'])
            return int(badge_text)
        else:
            return 0

    @keyword
    def go_to_cart(self):
        """
        Navigate to the shopping cart page.
        """
        browser = self._get_browser_library()
        browser.click(self.selectors['shopping_cart'])
        self.logger.info("Navigated to cart page")

    @keyword
    def logout(self):
        """
        Log out from the application.
        """
        browser = self._get_browser_library()
        
        # Open the burger menu
        browser.click(self.selectors['burger_menu'])
        
        # Wait for the logout link to be visible
        self.element_should_be_visible(self.selectors['logout_link'])
        
        # Click the logout link
        browser.click(self.selectors['logout_link'])
        self.logger.info("Logged out from the application")

    @keyword
    def get_product_prices(self):
        """
        Get the prices of all products on the page.
        
        Returns:
            list: List of product prices (as floats)
        """
        browser = self._get_browser_library()
        
        # Get all price elements
        price_elements = browser.get_elements(self.selectors['inventory_item_price'])
        
        # Extract text and convert to float
        prices = []
        for element in price_elements:
            price_text = browser.get_text(element)
            # Remove $ and convert to float
            price = float(price_text.replace('$', ''))
            prices.append(price)
            
        self.logger.info(f"Found product prices: {prices}")
        return prices 