from config import SCREEN_HEIGHT, SCREEN_WIDTH, CHAR_INFO_WIDTH, MAP_WIDTH, MAP_HEIGHT, LIMIT_FPS
import globals as g
import libtcodpy as libtcod
import textwrap

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 20

def char_info_window(c): # c == character
	width = CHAR_INFO_WIDTH
	
	header = "Character Information"
	
	char_attrs = [
				('Name', c.name),
				('Level', c.level),
				('XP', c.xp)
				]
	if c.combatant:
		combat_attrs = [
					('HP', c.combatant.hp),
					('Max HP', c.combatant.max_hp),
					('Attack power', c.combatant.power),
					('Defense power', c.combatant.defense)
					]
	if c.caster:
		caster_attrs = [
					('MP', c.caster.mp),
					('Max MP', c.caster.max_mp),
					('Hot/Cold factor', c.caster.hot_cold),
					('Wet/Dry factor', c.caster.wet_dry)
					]
	
	# calculate total height for the header (after auto-wrap) and one line per attr,
	# plus 2 for each section header (because of the preceding empty line), 4 extra in total
	header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
	height = len(char_attrs + combat_attrs + caster_attrs) + header_height + 4
	
	#create an off-screen console that represents the menu's window
	window = libtcod.console_new(width, height)

	#print the header, with auto-wrap
	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_print_rect(window, 0, 0, width, height, header)

	# print all the attributes
	y = header_height
	for attr in char_attrs:
		text = attr[0] + ': ' + str(attr[1])
		libtcod.console_print(window, 0, y, text)
		y += 1
		
	y += 1 # empty line
	libtcod.console_print(window, 0, y, 'Combatant attributes')
	y += 1
	
	for attr in combat_attrs:
		text = attr[0] + ': ' + str(attr[1])
		libtcod.console_print(window, 0, y, text)
		y += 1
		
	y += 1 # empty line
	libtcod.console_print(window, 0, y, 'Caster attributes')
	y += 1
	
	for attr in caster_attrs:
		text = attr[0] + ': ' + str(attr[1])
		libtcod.console_print(window, 0, y, text)
		y += 1

	#blit the contents of "window" to the root console
	x = SCREEN_WIDTH / 2 - width / 2
	y = SCREEN_HEIGHT / 2 - height / 2
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

	#present the root console to the player
	libtcod.console_flush()

def menu(header, options, width, options_params=None):
	if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

	# calculate total height for the header (after auto-wrap) and one line per option
	header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
	height = len(options) + header_height

	# create an off-screen console that represents the menu's window
	window = libtcod.console_new(width, height)

	# print the header, with auto-wrap
	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_print_rect(window, 0, 0, width, height, header)

	# print all the options
	y = header_height
	letter_index = ord('a')
	
	longest_text = 0
	
	for option_text in options:
		text = '(' + chr(letter_index) + ') ' + option_text
		libtcod.console_print(window, 0, y, text)
		y += 1
		letter_index += 1
		
		if len(text) > longest_text:
			longest_text = len(text)
			
	libtcod.console_vline(window, 3, header_height, height, libtcod.BKGND_LIGHTEN) # draw a line between the letter and the option
	
	if options_params:
		y = header_height
		last_char_x = longest_text
		libtcod.console_vline(window, last_char_x, header_height, height, libtcod.BKGND_LIGHTEN) # draw a line after the last column
		for param in options_params:
			libtcod.console_print(window, last_char_x+1, y, str(param))
			y += 1
			if len(str(param)) > longest_text:
				longest_text = len(str(param))
			

	# blit the contents of "window" to the root console
	x = SCREEN_WIDTH / 2 - width / 2
	y = SCREEN_HEIGHT / 2 - height / 2
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

	# present the root console to the player
	libtcod.console_flush()
"""
def info_popup(header, info):
	#Display info at mouse position.
	width = INFO_POPUP_WIDTH
	
	# calculate total height for the header (after auto-wrap) and one line per info piece
	header_height = libtcod.console_height_left_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
	height = len(info) + header_height
	
	window = libtcod.console_new(width, height)
	
	# print the header, with auto-wrap
	libtcod.console_set_foreground_color(window, libtcod.white)
	libtcod.console_print_left_rect(window, 0, 0, width, height, libtcod.BKGND_NONE, header)
	
	# print the info
	y = header_height
	for text in info:
		libtcod.console_print_left(window, 0, y, libtcod.BKGND_NONE, text)
		y += 1
	
	#blit the contents of "window" to the root console
	x = libtcod.mouse_get_status().x
	y = libtcod.mouse_get_status().y
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

	#present the root console to the player
	libtcod.console_flush()
"""
def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
	# render a bar (HP, experience, etc). first calculate the width of the bar
	bar_width = int(float(value) / maximum * total_width)
	
	# render the background first
	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SET)

	# now render the bar on top
	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SET)

	# finally, some centered text with the values
	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
		name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse():
	#return a string with the names of all objects under the mouse
	#libtcod.console_flush()
	libtcod.sys_check_for_event(libtcod.EVENT_ANY, key_event_structure, mouse_event_structure)
	(x, y) = (mouse_event_structure.cx, mouse_event_structure.cy)

	#create a list with the names of all objects at the mouse's coordinates and in FOV
	objects = []
	objects.extend(g.actors)
	objects.extend(g.items)
	objects.extend(g.terrain_features)
	
	names = []
	names.extend([obj.name for obj in objects
		if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)])

	names = ', '.join(names)  #join the names, separated by commas
	return names.capitalize()

def message(new_msg, color=libtcod.white):
	#split the message if necessary, among multiple lines
	new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

	for line in new_msg_lines:
		#if the buffer is full, remove the first line to make room for the new one
		if len(g.game_msgs) == MSG_HEIGHT:
			del g.game_msgs[0]

		#add the new line as a tuple, with the text and the color
		g.game_msgs.append((line, color))

def render_all():
	import Object
	
	if g.fov_recompute:
		#recompute FOV if needed (the player moved or something)
		g.fov_recompute = False
		libtcod.map_compute_fov(fov_map, Object.player.x, Object.player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

		#go through all tiles, and set their background color according to the FOV
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
				visible = libtcod.map_is_in_fov(fov_map, x, y)
				if not visible:
					#if it's not visible right now, the player can only see it if it's explored
					if g.level_map[y][x].explored:
						libtcod.console_set_char_background(con, x, y, g.level_map[y][x].color_out_FOV, libtcod.BKGND_SET)
				else:
					#it's visible
					libtcod.console_set_char_background(con, x, y, g.level_map[y][x].color_in_FOV, libtcod.BKGND_SET)
					#since it's visible, explore it
					g.level_map[y][x].explored = True

	# draw everything, starting with things most in the background
	for feature in g.terrain_features:
		feature.draw()
	for item in g.items:
		item.draw()
	for actor in g.actors:
		if actor != Object.player:
			actor.draw()
	Object.player.draw()

	#blit the contents of "con" to the root console
	libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

	#prepare to render the GUI panel
	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)

	#print the game messages, one line at a time
	y = 1
	for (line, color) in g.game_msgs:
		libtcod.console_set_default_foreground(panel, color)
		libtcod.console_print(panel, MSG_X, y, line)
		y += 1

	#show the player's stats
	render_bar(1, 1, BAR_WIDTH, 'HP', Object.player.combatant.hp, Object.player.combatant.max_hp, #@UndefinedVariable
		libtcod.light_red, libtcod.darker_red)
	render_bar(1, 2, BAR_WIDTH, 'MP', Object.player.caster.mp, Object.player.caster.max_mp, #@UndefinedVariable
		libtcod.light_blue, libtcod.darker_blue)

	#display names of objects under the mouse
	libtcod.console_set_default_foreground(panel, libtcod.light_gray)
	libtcod.console_print(panel, 1, 0, get_names_under_mouse())

	#blit the contents of "panel" to the root console
	libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
	
	libtcod.console_flush()
	
	#erase all actors at their old locations
	for actor in g.actors:
		actor.clear()

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod roguelike', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
mouse_event_structure = libtcod.Mouse()
key_event_structure = libtcod.Key()

#create the FOV map, according to the generated map and its objects
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)