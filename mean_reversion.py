import yfinance as yf
import numpy as np
from ibapi.client import EClient 
from ibapi.wrapper import EWrapper
from ibapi.contract import *
from ibapi.order import *

import datetime
import queue
import threading

# Below is TestApp Class 

class IBAPIWrapper(EWrapper):
    """
    A derived subclass of the IB API EWrapper interface
    that allows more straightforward response processing
    from the IB Gateway or an instance of TWS.
    """

    def init_error(self):
        """
        Place all of the error messages from IB into a
        Python queue, which can be accessed elsewhere.
        """
        error_queue = queue.Queue()
        self._errors = error_queue

    def is_error(self):
        """
        Check the error queue for the presence
        of errors.

        Returns
        -------
        `boolean`
            Whether the error queue is not empty
        """
        return not self._errors.empty()

    def get_error(self, timeout=5):
        """
        Attempts to retrieve an error from the error queue,
        otherwise returns None.

        Parameters
        ----------
        timeout : `float`
            Time-out after this many seconds.

        Returns
        -------
        `str` or None
            A potential error message from the error queue.
        """
        if self.is_error():
            try:
                return self._errors.get(timeout=timeout)
            except queue.Empty:
                return None
        return None

    def error(self, id, errorCode, errorString):
        """
        Format the error message with appropriate codes and
        place the error string onto the error queue.
        """
        error_message = (
            "IB Error ID (%d), Error Code (%d) with "
            "response '%s'" % (id, errorCode, errorString)
        )
        self._errors.put(error_message)

    def init_time(self):
        """
        Instantiates a new queue to store the server
        time, assigning it to a 'private' instance
        variable and also returning it.

        Returns
        -------
        `Queue`
            The time queue instance.
        """
        time_queue = queue.Queue()
        self._time_queue = time_queue
        return time_queue

    def currentTime(self, server_time):
        """
        Takes the time received by the server and
        appends it to the class instance time queue.

        Parameters
        ----------
        server_time : `str`
            The server time message.
        """
        self._time_queue.put(server_time)

# ib_api_connection.py

class IBAPIClient(EClient):
    """
    Used to send messages to the IB servers via the API. In this
    simple derived subclass of EClient we provide a method called
    obtain_server_time to carry out a 'sanity check' for connection
    testing.

    Parameters
    ----------
    wrapper : `EWrapper` derived subclass
        Used to handle the responses sent from IB servers
    """

    MAX_WAIT_TIME_SECONDS = 10

    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

    def obtain_server_time(self):
        """
        Requests the current server time from IB then
        returns it if available.

        Returns
        -------
        `int`
            The server unix timestamp.
        """
        # Instantiate a queue to store the server time
        time_queue = self.wrapper.init_time()

        # Ask IB for the server time using the EClient method
        self.reqCurrentTime()

        # Try to obtain the latest server time if it exists
        # in the queue, otherwise issue a warning
        try:
            server_time = time_queue.get(
                timeout=IBAPIClient.MAX_WAIT_TIME_SECONDS
            )
        except queue.Empty:
            print(
                "Time queue was empty or exceeded maximum timeout of "
                "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
            )
            server_time = None

        # Output all additional errors, if they exist
        while self.wrapper.is_error():
            print(self.get_error())

        return server_time

# ib_api_connection.py

class IBAPIApp(IBAPIWrapper, IBAPIClient):
    """
    The IB API application class creates the instances
    of IBAPIWrapper and IBAPIClient, through a multiple
    inheritance mechanism.

    When the class is initialised it connects to the IB
    server. At this stage multiple threads of execution
    are generated for the client and wrapper.

    Parameters
    ----------
    ipaddress : `str`
        The IP address of the TWS client/IB Gateway
    portid : `int`
        The port to connect to TWS/IB Gateway with
    clientid : `int`
        An (arbitrary) client ID, that must be a positive integer
    """

    def __init__(self, ipaddress, portid, clientid):
        IBAPIWrapper.__init__(self)
        IBAPIClient.__init__(self, wrapper=self)

        # Connects to the IB server with the
        # appropriate connection parameters
        self.connect(ipaddress, portid, clientid)

        # Initialise the threads for various components
        thread = threading.Thread(target=self.run)
        thread.start()
        setattr(self, "_thread", thread)

        # Listen for the IB responses
        self.init_error()

def contractCreate():
    # Fills out the contract object
    contract = Contract()  # Creates a contract object from the import
    contract.symbol = "TSLA"   # Sets the ticker symbol 
    contract.secType = "STK"   # Defines the security type as stock
    contract.currency = "USD"  # Currency is US dollars 
    # In the API side, NASDAQ is always defined as ISLAND in the exchange field
    contract.exchange = "SMART"
    # contract.PrimaryExch = "NYSE"
    return contract    # Returns the contract object

def orderCreateBuy():
    # Fills out the order object 
    order = Order()    # Creates an order object from the import
    order.action = "BUY"   # Sets the order action to buy
    order.orderType = "MKT"    # Sets order type to market buy
    order.transmit = True
    order.totalQuantity = 10   # Setting a static quantity of 10 
    return order   # Returns the order object 

def orderCreateSell():
    # Fills out the order object 
    order = Order()    # Creates an order object from the import
    order.action = "Sell"   # Sets the order action to buy
    order.orderType = "MKT"    # Sets order type to market buy
    order.transmit = True
    order.totalQuantity = 10   # Setting a static quantity of 10 
    return order   # Returns the order object 

def orderExecutionBuy():
    #Places the order with the returned contract and order objects 
    contractObject = contractCreate()
    orderObject = orderCreateBuy()
    nextID = 101
    print("The next valid id is - " + str(nextID))
    app.placeOrder(nextID, contractObject, orderObject)
    print("Buy order was placed")

def orderExecutionSell():
    #Places the order with the returned contract and order objects 
    contractObject = contractCreate()
    orderObject = orderCreateSell()
    nextID = 101
    print("The next valid id is - " + str(nextID))
    app.placeOrder(nextID, contractObject, orderObject)
    print("Sell order was placed")

# Below is the program execution

# ib_api_connection.py

if __name__ == '__main__':
    # Application parameters
    host = '127.0.0.1'  # Localhost, but change if TWS is running elsewhere
    port = 7497  # Change to the appropriate IB TWS account port number
    client_id = 1

    print("Launching IB API application...")

    # Instantiate the IB API application
    app = IBAPIApp(host, port, client_id)

    print("Successfully launched IB API application...")

    # Obtain the server time via the IB API app
    server_time = app.obtain_server_time()
    server_time_readable = datetime.datetime.utcfromtimestamp(
        server_time
    ).strftime('%Y-%m-%d %H:%M:%S')

    print("Current IB server time: %s" % server_time_readable)

    # Disconnect from the IB server
    app.disconnect()

    print("Disconnected from the IB API application. Finished.")

# Define the period and the rolling window size
period = '1d'
window = 20

# Download the historical data for Tesla
tesla = yf.Ticker("TSLA")
data = tesla.history(period=period)

# Compute the rolling mean
data['rolling_mean'] = data['Close'].rolling(window=window).mean()

# Define the trading strategy
while True:
    # Get the latest data
    data = tesla.history(period=period)
    data['rolling_mean'] = data['Close'].rolling(window=window).mean()
    
    # Check if the current price is below the rolling mean
    if data['Close'].iloc[-1] < data['rolling_mean'].iloc[-1]:
        # Short Tesla
        orderExecutionSell()
    else:
        # Long Tesla
        orderExecutionBuy()