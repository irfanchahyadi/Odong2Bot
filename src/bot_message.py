MESSAGE = {
	'welcome': 
	"""*Odong2 Online Shop*\nWelcome to our shop, we provide a lot of high quality product.\nSimple order process, you just sit in your favorite chair and we deliver to your front door.\nPress this menu button.""",

	'list_product':
	"List our product",

	'added_cart':
	"Your order has been added to your cart",

	'removed_cart':
	"Your order has been removed",

	'updated_cart':
	"Your order has been updated",

	'checkout':
	"For deliver your order, we need your location"
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
	  [{'text':'Cancel', 'callback_data':'Cancel'}]],

	 'cart':
	 [[{'text':'Edit', 'callback_data':'EditCart'}, {'text':'Check Out', 'callback_data':'CheckOut'}]],

	 'checkout':
	 [[{'text':'Send your location', 'callback_data':'SendLocation'}]],	 
}