import os
import argparse
from urllib.parse import urlparse, parse_qs
from lxml.html import fromstring
from requests import get

PRODUCTS_FILE = "products.txt"


def main():
    """ Start of the program. """
    parser_description = "Find or retrieve a list of saved products"
    parser = argparse.ArgumentParser(description=parser_description)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--product", action="store", nargs=1, type=str,
                       metavar="PRODUCT",
                       help="Find information about a product")
    group.add_argument("-f", "--find", action="store", nargs=1, type=str,
                       metavar="PRODUCT",
                       help="Find the best price for a product")
    group.add_argument("-r", "--retrieve", action="store_true",
                       help="Retrieve a list of saved products and prices")
    args = parser.parse_args()

    # Retrieve saved products and their prices
    if args.retrieve is not False:
        retrieve_products()
    elif args.product:
        get_product_info(args.product)
    elif args.find:
        pass
    else:
        print("Select from the following:\n"
              "('P') - Find information about a product\n"
              "('F') - Find a specific product\n"
              "('R') - Retrieve a list of saved products\n")
        user_selection = input(">> ")

        if user_selection.lower() == "r":
            retrieve_products()
            return
        else:
            product_name = input("Enter the product name\n>> ")
            if user_selection.lower() == 'p':
                args.product = product_name
            elif user_selection.lower() == 'f':
                args.find = product_name
            else:
                print("No product name entered.")
    # Find a requested product and print the best prices
    if args.find:
        product = args.find[0]
        print("** Finding the best prices for you now... **")
        if find(product) is not None:
            name, url, prices = find(product)
        else:
            return
        print(f"\n{name}\n{url}")
        print("Here are the 10 best prices that have been found:")

        lowest_price = ""
        for price in prices:
            if prices.index(price) == 0:
                lowest_price = price
            if prices.index(price) > 9:
                break
            index = prices.index(price) + 1
            print(f"{index}. ${price[1]:.2f} from {price[0]}")

        do_save = input("Do you want to save the best price? (y/n)\n>> ")
        if do_save.lower() == "y":
            print("Saving price...")
            save(name, lowest_price, url)
    if args.product:
        product = args.product
        if get_product_info(product)[0]:
            product_name, description = get_product_info(product)
        else:
            return
        if len(description) > 0:
            print("** Getting the product description for you now... **")
            print(f"\n{product_name} - Product Description\n")
            for line in description:
                print(line)
        else:
            print("No product description was found for this product.")

    print("--- Rerun the program to retrieve saved products and prices"
          " or to find the best price of a new product! ---")


def get_product_info(product):
    product_url = get_product_url(product)

    raw = get(product_url).text
    page = fromstring(raw)

    if len(page.cssselect("#productName")) <= 0:
        print("Your product is too generic, you must enter a more"
              " specific product name.")
        return

    if len(page.cssselect(".rpl-retailer")) <= 0:
        print("Your product could not be found!")
        return

    name = page.cssselect("#productName")[0].text

    info = []
    for item in page.cssselect(".panel-body.divAttGroup.fontlarger p"):
        paragraph = item.text_content().split('.')
        for line in paragraph:
            if len(line) > 1:
                info.append(f"{line.strip()}.")
        info.append('')

    return name, info


def get_product_url(product):
    search_url = f"https://www.google.com/search?q={product}" \
        f"+site:https://www.priceme.co.nz"

    raw = get(search_url).text
    page = fromstring(raw)

    product_url = ""
    for result in page.cssselect("a"):
        url = result.get("href")
        if url.startswith("/url?"):
            url = parse_qs(urlparse(url).query)['q']
            if any("https://www.priceme.co.nz/" in s for s in url):
                product_url = url[0]
                break
    return product_url


def find(product):
    """
    Finds a product on the priceme site and returns its information.

    :param product:
    :return list: str product_name: The proper name of the product.,
                  str product_url: The url of the product.,
                  list sorted_prices: Lowest to highest prices.
    """
    if get_product_url(product):
        product_url = get_product_url(product)
    else:
        print("Your product could not be found!")
        return

    raw = get(product_url).text
    page = fromstring(raw)

    if get_product_info(product):
        product_name, product_info = get_product_info(product)
    else:
        return

    companies = []
    for result in page.cssselect(".rpl-retailer"):
        retailers_name = ""
        retailers_logo = result.cssselect(".rpl-retailerlog")
        if len(retailers_logo) > 0:
            img_obj = result.cssselect(".rpl-retailerlog amp-img")
            retailers_name = img_obj[0].get("alt")

        name_obj = result.cssselect(".rpl-retailername")
        if len(name_obj) > 0:
            retailers_name = name_obj[0].text

        if len(retailers_name) > 0:
            companies.append(retailers_name.strip("\n "))

    all_prices = []
    prices = page.cssselect(".rpl-psvs-price")
    for i in prices:
        price = i.cssselect(".PriceLarge.nolinkPrice span")
        if len(price) > 0:
            all_prices.append(float(price[1].text.replace(',', '') +
                                    price[2].text))

        price = i.cssselect(".PriceLarge.rplistPrice span")
        if len(price) > 0:
            all_prices.append(float(price[1].text.replace(',', '') +
                                    price[2].text))

    info = zip(companies, all_prices)
    sorted_prices = sorted(info, key=lambda t: t[1])

    if len(sorted_prices) <= 0:
        print("You must enter a more specific product name and not category.")
        return

    return [product_name, product_url, sorted_prices]


def retrieve_products():
    """
    Prints a list of all saved products with their price and the seller.

    :return None:
    """
    print("** Retrieving your saved prices for you now... **")
    with open(PRODUCTS_FILE, 'r') as file:
        for line in file.readlines():
            if line == '\n':
                continue
            item, store, price, url = [x.strip("(\')").strip()
                                       for x in line.split(',')]
            price = float(price)
            print(f"Item: {item} - Price: ${price:.2f} - Store: {store}")


def save(product_name, price, link):
    """
    Saves a product with it's priceme link to a text file.

    :param str product_name: The name of the product.
    :param str price: The price of the product.
    :param str link: The url of the product.
    :return None:
    """
    if os.path.isfile(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r') as file:
            for entry in file.readlines():
                items = [x for x in entry.split(',')]
                # Disallow duplicate values
                if link in items or f"{link}\n" in items:
                    return
    else:
        # Create the file if it does not exist
        with open(PRODUCTS_FILE, 'w'):
            pass

    with open(PRODUCTS_FILE, 'a') as file:
        product_info = f"{product_name},{price},{link}"
        file.write('\n' + product_info)


if __name__ == '__main__':
    main()
