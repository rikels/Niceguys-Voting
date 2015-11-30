##source: http://timgolden.me.uk/python/win32_how_do_i/catch_system_wide_hotkeys.html
import os
import sys
import ctypes
from ctypes import wintypes
import win32con
#I was testing a little, and when you hold the button for too long... shit will shlowww down drastically
#that's why i import time, so i can use sleep() after a function has been called, so it won't spam 1000 messages which all need to be received and processed
import time


def listen(connection_to_mom):
	if connection_to_mom.readable:
		byref = ctypes.byref
		user32 = ctypes.windll.user32
		keys = connection_to_mom.recv()
		#dictionary with all possible keys i could find and map to keys on my keyboard (haven't tested all of them though)
		#this is purely so we can translate human readable keys to the correct Win32Con mapping
		#there are still Win32con keys available that I haven't used, as I couldn't find those keys on my keyboard, or wasn't sure what the heck it is.
		keymap = {
			"enter": win32con.VK_RETURN,
			"up": win32con.VK_UP,
			"down": win32con.VK_DOWN,
			"left": win32con.VK_LEFT,
			"right": win32con.VK_RIGHT,
			"backspace": win32con.VK_BACK,
			"delete": win32con.VK_DELETE,
			"end": win32con.VK_END,
			"home": win32con.VK_HOME,
			"tab": win32con.VK_TAB,
			"f1": win32con.VK_F1,
			"f2": win32con.VK_F2,
			"f3": win32con.VK_F3,
			"f4": win32con.VK_F4,
			"f5": win32con.VK_F5,
			"f6": win32con.VK_F6,
			"f7": win32con.VK_F7,
			"f8": win32con.VK_F8,
			"f9": win32con.VK_F9,
			"f10": win32con.VK_F10,
			"f11": win32con.VK_F11,
			"f12": win32con.VK_F11,
			"f13" : win32con.VK_F13,
			"f14" : win32con.VK_F14,
			"f15" : win32con.VK_F15,
			"f16" : win32con.VK_F16,
			"f17" : win32con.VK_F17,
			"f18" : win32con.VK_F18,
			"f19" : win32con.VK_F19,
			"f20" : win32con.VK_F20,
			"f21" : win32con.VK_F21,
			"f22" : win32con.VK_F22,
			"f23" : win32con.VK_F23,
			"f24" : win32con.VK_F24,
			"pageup": win32con.VK_PRIOR,
			"pagedown": win32con.VK_NEXT,
			"escape": win32con.VK_ESCAPE,
			"left mouse" : win32con.VK_LBUTTON,
			"right mouse" : win32con.VK_RBUTTON,
			"control break" : win32con.VK_CANCEL,
			"middle mouse" : win32con.VK_MBUTTON,
			"clear" : win32con.VK_CLEAR,
			"shift" : win32con.VK_SHIFT,
			"ctrl" : win32con.VK_CONTROL,
			"menu" : win32con.VK_MENU,
			"pause" : win32con.VK_PAUSE,
			"caps" : win32con.VK_CAPITAL,
			"space" : win32con.VK_SPACE,
			"end" : win32con.VK_END,
			"home" : win32con.VK_HOME,
			"print screen" : win32con.VK_SNAPSHOT,
			"insert" : win32con.VK_INSERT,
			"delete" : win32con.VK_DELETE,
			"windows" : win32con.MOD_WIN,
			"left windows" : win32con.VK_LWIN,
			"right windows" : win32con.VK_RWIN,
			"num0" : win32con.VK_NUMPAD0,
			"num1" : win32con.VK_NUMPAD1,
			"num2" : win32con.VK_NUMPAD2,
			"num3" : win32con.VK_NUMPAD3,
			"num4" : win32con.VK_NUMPAD4,
			"num5" : win32con.VK_NUMPAD5,
			"num6" : win32con.VK_NUMPAD6,
			"num7" : win32con.VK_NUMPAD7,
			"num8" : win32con.VK_NUMPAD8,
			"num9" : win32con.VK_NUMPAD9,
			"*" : win32con.VK_MULTIPLY,
			"+" : win32con.VK_ADD,
			"-" : win32con.VK_SUBTRACT,
			"" : win32con.VK_DECIMAL,
			"/" : win32con.VK_DIVIDE,
			"numlock" : win32con.VK_NUMLOCK,
			"scroll lock" : win32con.VK_SCROLL,
			"left shift" : win32con.VK_LSHIFT,
			"right shift" : win32con.VK_RSHIFT,
			"left ctrl" : win32con.VK_LCONTROL,
			"right ctrl" : win32con.VK_RCONTROL,
			"left menu" : win32con.VK_LMENU,
			"right menu" : win32con.VK_RMENU,
			"mouse wheel" : win32con.MOUSEEVENTF_WHEEL,
			"media mute" : win32con.VK_VOLUME_MUTE,
			"media vol down" : win32con.VK_VOLUME_DOWN,
			"media vol up" : win32con.VK_VOLUME_UP,
			"media next" : win32con.VK_MEDIA_NEXT_TRACK,
			"media prev" : win32con.VK_MEDIA_PREV_TRACK,
			"media play" : win32con.VK_MEDIA_PLAY_PAUSE,
			"prev page" : win32con.VK_BROWSER_BACK,
			"next page" : win32con.VK_BROWSER_FORWARD,
		#dunno what these are, if someone can clarify, I'll maybe add them :),
			"" : win32con.VK_SEPARATOR,
			"" : win32con.VK_KANA,
			"" : win32con.VK_HANGEUL,
			"" : win32con.VK_HANGUL,
			"" : win32con.VK_JUNJA,
			"" : win32con.VK_FINAL,
			"" : win32con.VK_HANJA,
			"" : win32con.VK_KANJI,
			"" : win32con.VK_CONVERT,
			"" : win32con.VK_NONCONVERT,
			"" : win32con.VK_ACCEPT,
			"" : win32con.VK_MODECHANGE,
			"" : win32con.VK_PRIOR,
			"" : win32con.VK_NEXT,
			"" : win32con.VK_SELECT,
			"" : win32con.VK_PRINT,
			"" : win32con.VK_EXECUTE,
			"" : win32con.VK_HELP,
			"" : win32con.VK_APPS,
			"" : win32con.VK_PROCESSKEY,
			"" : win32con.VK_ATTN,
			"" : win32con.VK_CRSEL,
			"" : win32con.VK_EXSEL,
			"" : win32con.VK_EREOF,
			"" : win32con.VK_PLAY,
			"" : win32con.VK_ZOOM,
			"" : win32con.VK_NONAME,
			"" : win32con.VK_PA1,
			"" : win32con.VK_OEM_CLEAR,
			# multi-media related
			"" : win32con.MOUSEEVENTF_XDOWN,
			"" : win32con.MOUSEEVENTF_XUP,
			"" : win32con.VK_XBUTTON1,
			"" : win32con.VK_XBUTTON2,
			}

		#if the user is using custom keys, we have to convert them, as we want to give users an easy option to set their keys,
		#so they don't need to now the win32con.VKF2 codes and such
		i = 1
		HOTKEYS = {}
		for key_combo in keys:
			HOTKEYS[i] = ()
			for key in key_combo:
				HOTKEYS[i] = HOTKEYS[i] + (keymap[key],)
			i += 1

	def handle_win_f2():
		#sending to parent process that the action, given 1 here, kind of randomly (ID's are better than names)
		connection_to_mom.send({"action": 1})

	def handle_win_f3():
		#sending to parent process that the action 2 should be run.
		connection_to_mom.send({"action": 2})

	def handle_win_f4():
		#sending to parent process that the action 2 should be run.
		connection_to_mom.send({"action": 3})

	HOTKEY_ACTIONS = {
		1 : handle_win_f2,
		2 : handle_win_f3,
		3 : handle_win_f4
	}

	#
	# RegisterHotKey takes:
	#  Window handle for WM_HOTKEY messages (None = this thread)
	#  arbitrary id unique within the thread
	#  modifiers (MOD_SHIFT, MOD_ALT, MOD_CONTROL, MOD_WIN)
	#  VK code (either ord ('x') or one of win32con.VK_*)
	#
	for id, (vk, modifiers) in HOTKEYS.items ():
		#print ("Registering id", id, "for key", vk)
		if not user32.RegisterHotKey (None, id, modifiers, vk):
			print ("Unable to register id", id)

	#
	# Home-grown Windows message loop: does
	#  just enough to handle the WM_HOTKEY
	#  messages and pass everything else along.
	#
	try:
		msg = wintypes.MSG ()
		while user32.GetMessageA (byref (msg), None, 0, 0) != 0:
			if msg.message == win32con.WM_HOTKEY:
				action_to_take = HOTKEY_ACTIONS.get (msg.wParam)
				if action_to_take:
					action_to_take ()
			user32.TranslateMessage (byref (msg))
			user32.DispatchMessageA (byref (msg))
	finally:
		for id in HOTKEYS.keys ():
			user32.UnregisterHotKey (None, id)