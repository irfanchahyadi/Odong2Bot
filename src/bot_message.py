MESSAGE = {
	'welcome': 
	"""*Odong2 Online Shop*
	Welcome to our shop, we provide a lot of high quality product.
	Simple order process, you just sit in your favorite chair and we deliver to your front door.
	Press this menu button.""",

	'list_product':
	"List our product",

	'added_cart':
	"Your order has been added to your cart"
}

KEYBOARD = {
	'product':
	[[{'text':'< Prev', 'callback_data':'Prev'}, {'text':'Order Product', 'callback_data':'OrderProduct'}, {'text':'Next >', 'callback_data':'Next'}],
	 [{'text':'Sort', 'callback_data':'Sort'}, {'text':'Search', 'callback_data':'Search'}, {'text':'Filter', 'callback_data':'Filter'}, {'text':'Clear', 'callback_data':'Clear'}]],

	 'sort_product':
	 [[{'text':'Sort by Highest Price', 'callback_data':'SortbyHighestPrice'}],
	  [{'text':'Sort by Lowest Price', 'callback_data':'SortbyLowestPrice'}],
	  [{'text':'Sort by Name A-Z', 'callback_data':'SortbyNameA-Z'}],
	  [{'text':'Sort by Name Z-A', 'callback_data':'SortbyNameZ-A'}],
	  [{'text':'Cancel', 'callback_data':'Cancel'}]]
}