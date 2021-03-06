import wx
import os
import copy
import random
import pygame
from pygame.locals import Color
from collections import OrderedDict
from pygamepanel import PygamePanel
import  wx.lib.newevent, wx.stc as stc
from statusctrl import StatusCtrl
from listener import Key_listener
from record import Record
import verts

from OpenGL.GL import *
from OpenGL.GLU import *

class OBJ2D:
	def __init__(self, dirname, HUD):
		self.HUD = HUD
		self.record = Record()
		self.data = {}
		self.data["speed"] = {"scale":.05,"b_amp":1}
		self.dirname = dirname
		self.width = 0
		self.height = 0
		self.frame_rate = 6
		self.texture_dict = {}
		self.portrait = None
		self.data["b_amp"] = 350
		self.data["effect"] = "scale"
		self.data["scale"] = 1
		self.data["angle"] = 0
		self.data["pos"] = [0,0,0]
		self.data["flipX"] = 1.0
		self.data["flipY"] = 1.0
		self.data["mouth"] = ord("z")
		self.data["substate"] = ord("a")
		self.data["state"] = ord("q")
		self.data["dir"] = pygame.K_DOWN
		self.data["visible"] = True
		self.data["frame"] = 0
		self.data["toggle"] = False
		self.data["boiler"] = 0
		self.frame_counter = 0
		self.changes = False
		self.verts = copy.deepcopy(verts.verts)

		self.coords = copy.deepcopy(verts.coords)

		self.edges = copy.deepcopy(verts.edges)
		self.cur_verts = copy.deepcopy(verts.verts)

	def load_all(self, dirname):
		self.dirname = dirname
		#mouth - z,x,c,v,b,n,m
		#state - q,w,e,r,t,y,u,i,o,p
		#substate - a,s,d,f,g,h,j,k,l
		#dirs - up, down, left, right

		mouth = ["z", "x", "c", "v", "b", "n", "m"]
		state = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
		substate = ["a", "s", "d", "f", "g", "h", "j", "k", "l"]
		dirs = {"up":pygame.K_UP, "down":pygame.K_DOWN, "left":pygame.K_LEFT, "right":pygame.K_RIGHT}

		fullpath = os.path.join("res", self.dirname)
		file_list = os.listdir(fullpath)
		if "portrait.png" in file_list:
			self.portrait = os.path.join(fullpath, "portrait.png")

		for mouth_key in mouth:
			if mouth_key in file_list:
				self.texture_dict[ord(mouth_key)] = {}
				mouth_file_list = os.listdir(os.path.join(fullpath, mouth_key))

				for state_key in state:
					if state_key in mouth_file_list:
						self.texture_dict[ord(mouth_key)][ord(state_key)] = {}
						state_file_list = os.listdir(os.path.join(fullpath, mouth_key, state_key))

						for substate_key in substate:
							if substate_key in state_file_list:
								self.texture_dict[ord(mouth_key)][ord(state_key)][ord(substate_key)] = {}
								substate_file_list = os.listdir(os.path.join(fullpath, mouth_key, state_key, substate_key))

								for Dir in dirs.keys():
									if Dir in substate_file_list:
										self.texture_dict[ord(mouth_key)][ord(state_key)][ord(substate_key)][dirs[Dir]] = self.load_textures(os.path.join(fullpath, mouth_key, state_key, substate_key, Dir))

	def get_portrait(self):
		return self.portrait

	def space_toggle(self, toggle):
		self.data["toggle"] = toggle
		self.changes = True

	def set_data(self):
		self.HUD.set_Animating(True)
		self.HUD.set_yoffset(0)
		self.HUD.set_xoffset(0)
		self.HUD.set_playback(self.record.is_playing())
		self.HUD.set_recording(self.record.is_recording())
		self.HUD.set_mouth(self.data["mouth"])
		self.HUD.set_substate(self.data["substate"])
		self.HUD.set_state(self.data["state"])
		self.HUD.set_angle(self.data["angle"])
		self.HUD.set_pos(self.data["pos"])
		self.HUD.set_FLIP_H(self.data["flipX"])
		self.HUD.set_FLIP_V(self.data["flipY"])
		self.HUD.set_Speed(self.data["speed"]["scale"])

	def boil(self):
		self.data["effect"] = "b_amp"
		self.changes = True

	def scale(self):
		self.data["effect"] = "scale"
		self.changes = True

	def update(self):
		if self.record.is_recording():
			self.record.append(self.data)
		elif self.record.is_playing():
			self.data = self.record.get()
			self.record.next()
		#if self.changes and self.dirname != None:
		#	self.data["frame"] = (self.data["frame"] + 1) % len(self.texture_dict[self.data["mouth"]][self.data["state"]][self.data["substate"]][self.data["dir"]])
		self.changes = False

	def set_mouth(self, mouth):
		if mouth in self.texture_dict.keys():
			self.data["mouth"] = mouth
		self.changes = True

	def set_state(self, state):
		if state in self.texture_dict[self.data["mouth"]].keys():
			self.data["state"] = state
		self.changes = True

	def set_substate(self, substate):
		if substate in self.texture_dict[self.data["mouth"]][self.data["state"]].keys():
			self.data["substate"] = substate
		self.changes = True

	def set_dir(self, Dir):
		if Dir in self.texture_dict[self.data["mouth"]][self.data["state"]][self.data["substate"]].keys():
			self.data["dir"] = Dir
		self.changes = True

	def zoom(self, factor):
		self.data[self.data["effect"]] += self.data["speed"][self.data["effect"]] * factor
		self.data[self.data["effect"]] = self.data[self.data["effect"]] % 500
		print(self.data[self.data["effect"]])
		self.changes = True

	def flipX(self):
		self.data["flipX"] *= -1.0
		self.changes = True

	def flipY(self):
		self.data["flipY"] *= -1.0
		self.changes = True

	def start_recording(self):
		self.record.start()
		self.changes = True

	def stop_recording(self):
		self.record.pause()
		self.changes = True

	def start_playing(self):
		if self.record.has_recorded():
			self.record.playback()
		self.changes = True

	def stop_playing(self):
		if self.record.has_recorded():
			self.record.stop()
		self.changes = True

	def clear(self):
		self.record.clear()

	def places(self):
		self.record.reset()

	def m_rot(self, m_rel):
		self.data["angle"] -= m_rel[0] * .5
		self.changes = True

	def rotp(self):
		self.data["angle"] += self.data["speed"]["scale"] * 100
		self.changes = True

	def rotn(self):
		self.data["angle"] += self.data["speed"]["scale"] * -100
		self.changes = True

	def set_pos(self, pos):
		self.data["pos"] = [pos[0], pos[1], self.data["pos"][2]]
		self.changes = True

	def move_H(self, delta):
		self.data["pos"][0] += delta * self.data["speed"]["scale"]
		self.changes = True

	def move_V(self, delta):
		self.data["pos"][1] += delta * self.data["speed"]["scale"]
		self.changes = True

	def move_D(self, delta):
		self.data["pos"][2] += delta * self.data["speed"]["scale"]
		self.changes = True

	def set_name(self, name):
		self.dirname = name
		self.changes = True

	def load_textures(self, dirname):
		text_list = []
		names = os.listdir(dirname)
		for name in names:
			text_list.append(self.load_texture(os.path.join(dirname, name)))
		return text_list

	def load_texture(self, name):

		textureSurface = pygame.image.load(name).convert_alpha()
		textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
		self.width = textureSurface.get_width()
		self.height = textureSurface.get_height()

		if self.width > self.height:
			ratio = self.height/self.width
			for x in range(len(self.verts)):
				self.verts[x][1] *= ratio

		else:
			ratio = self.width/self.height
			for x in range(len(self.verts)):
				self.verts[x][0] *= ratio

		glEnable(GL_TEXTURE_2D)

		texid = glGenTextures(1)

		glBindTexture(GL_TEXTURE_2D, texid)
		
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height,
					 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		
		glGenerateMipmap(GL_TEXTURE_2D)
		
		return texid

	def draw_surf(self):
		glPushMatrix()
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_BLEND)

		glTranslatef(self.data["pos"][0], self.data["pos"][1] , self.data["pos"][2])
		glRotatef(self.data["angle"], 0, 0, 1)
		glScalef(self.data["flipX"] * self.data["scale"],self.data["flipY"] * self.data["scale"],1.0)
		#self.data["angle"] = 0
		glBegin(GL_POLYGON)

		#establishes a wobble in the character, a subtle but cheap replacement for boiling lines
		if self.data["b_amp"] > 0:
			self.data["boiler"] += 1
			if self.data["boiler"] % 5 == 0:
				self.cur_verts = []
				for x in range(len(self.verts)):
					if x not in [0,1,len(self.verts)-1,len(self.verts)-2]:
						self.cur_verts.append([(self.verts[x][0]+(random.random())/(500-self.data["b_amp"])),(self.verts[x][1]+(random.random())/(500-self.data["b_amp"])),self.verts[x][2]])
					else:
						self.cur_verts.append([self.verts[x][0],self.verts[x][1],self.verts[x][2]])					
		else:
			self.cur_verts = self.verts


		for x in range(len(self.verts)):
			glTexCoord2f(*self.coords[x])
			glVertex3f(*self.cur_verts[x])

		glEnd()

		glDisable(GL_BLEND)
		glPopMatrix()

	def draw_entity(self):
		if self.dirname != None and self.data["visible"]:
			if self.data["toggle"] and (pygame.K_x in self.texture_dict.keys()):
				self.frame_counter += 1
				if self.frame_counter >= self.frame_rate:
					self.frame_counter = 0
					self.data["frame"] = random.randrange(100)#(self.data["frame"] + 1)

				self.data["frame"] = self.data["frame"] % len(self.texture_dict[pygame.K_x][self.data["state"]][self.data["substate"]][self.data["dir"]])

				glBindTexture(GL_TEXTURE_2D, self.texture_dict[pygame.K_x][self.data["state"]][self.data["substate"]][self.data["dir"]][self.data["frame"]] )
			else:
				self.frame_counter += 1
				if self.frame_counter >= self.frame_rate:
					self.frame_counter = 0

					self.data["frame"] = (self.data["frame"] + 1)

				self.data["frame"] = self.data["frame"] % len(self.texture_dict[self.data["mouth"]][self.data["state"]][self.data["substate"]][self.data["dir"]])

				glBindTexture(GL_TEXTURE_2D, self.texture_dict[self.data["mouth"]][self.data["state"]][self.data["substate"]][self.data["dir"]][self.data["frame"]] )

			self.draw_surf()

	def draw_wire(self):
		glPushMatrix()
		glTranslatef(self.data["pos"][0], self.data["pos"][1] , self.data["pos"][2])
		glRotatef(self.data["angle"], 0, 0, 1)

		glBegin(GL_LINES)
		for Edge in self.edges:
			for Vertex in Edge:
				glVertex3fv(self.verts[Vertex])
		glEnd()
		glPopMatrix()	