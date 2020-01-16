# Price Finder
This script allows the user to find and retrieve the best prices for different products through [PriceMe](https://www.priceme.co.nz/).

## Getting Started

Once downloaded, run main.py using the command-line to start the script.

### Prerequisites

To use this script you will need the following:

```
Python 3.6+
lxml 4.3.4+
requests 2.22+
cssselect 1.0.3+
```

For developing and testing it is best to use a virtual environment and will require:
```
virtualenv 16.6.1+
```


### Usage

##### Running the program

To run the program, run the following command where "PRODUCT" is the name of the product you wish to find.

**Example:**
*Find Product*
```
C:\>python price-finder -f [--find] PRODUCT
```

**Example:**
*Product Description*
```
C:\>python price-finder -p [--product] PRODUCT
```

**Other commands can be found with:** *Help*
```
C:\>python price-finder main.py [-h] [--help]
```

## Built With

* [Python 3.6](https://docs.python.org/3.6/) - The programming language used.
* [lxml 4.3.4](https://pypi.org/project/lxml/) - The library used by the script to get html content.
* [requests 2.22.0](https://pypi.org/project/lxml/) - The library used by the script to process html content.


## Author

**Joshua Booth** - [Joshua-Booth](https://github.com/Joshua-Booth)
