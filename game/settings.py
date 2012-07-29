'''
This module imports all the graphics/animations and makes them globally available to the rest of the code.

The sounds should probably be moved here too.
'''
from animation import Image, Animation, LoopingAnimation
#import pygame.mixer

        
class Images:
    def __init__(self, dir):
        self.images = dict()

        self.images["resource_pool"] = Image(dir.child("resource").child("resource_pool.png"))
        self.images["resource_pool_zone"] = Image(dir.child("resource").child("resource_zone.png"))
        
        self.images["background"] = Image(dir.child("other").child("bg_tile.png"))
        self.images["Attack"] = Animation(dir.child("players").child("attack").child("attack%04d.png"))
        self.images["LevelUp"] = Animation(dir.child("effects").child("player_lvlup").child("player_lvlup%04d.png"))


        self.images["player upgraded"] = Animation(dir.child("effects").child("player_lvlup").child("player_lvlup%04d.png"))
        
        self.images["mining"] =Animation(dir.child("effects").child("resource_gather").child("resource_gather%04d.png"))

        self._initPlayerImages(dir)
        self._initBuildingImages(dir)
        self._initArmorImages(dir)
        


    def _initPlayerImages(self, dir):
        
        #Warning: old scan
        self.images["PlayerScan"] = Image(dir.child("players").child("scan").child("player_scan.png"))
        self.images["SentryScan"] = Image(dir.child("buildings").child("sentry").child("sentry_zones").child("sentry_vision.png"))
        
        teamDir = dir.child("players").child("polygons")
        sides = {0 : "dot", 1 : "line", 2 : "cross", 3 : "tri", 4 : "sqr", 5 : "pent", 6 : "hex"}
        
        #offsets = {"dot" : (0,0), "line" : (0,0), "cross" : (0,0), "tri" : (0,-5), "sqr" : (0,0), "pent" : (0,0), "hex" : (0,0)}
        offsets = {0 : (0,0), 1 : (0,0), 2 : (0,0), 3 : (0,0), 3 : (0,3), 4 : (0,0), 5 : (0,0), 6 : (0,0)}
        
        firstPerson = {1:"red", 2:"blue"}
        for p in firstPerson:
            for s in sides:
                path = teamDir.child(sides[s]).child("%s_%s.png" % (sides[s], firstPerson[p]))
                self.images["Player", p, s] = Image(path, offsets[s])
            self.images["Enemy", p] = LoopingAnimation(
                    teamDir.child("unidentified").child("%s" % (firstPerson[p])).child(firstPerson[p]+"_unidentified%04d.png")
                                                             )

    def _initBuildingImages(self, dir):
        buildingsDir = dir.child("buildings")

        resource1 = Image(dir.child("resource").child("resource01.png"))
        resource2 = Image(dir.child("resource").child("resource02.png"))

        teammate = {1 : "_red", 2 : "_blue"}
        sides = {3 : "trap", 4 : "sentry", 5 : "polyfactory"}
        healthOffsets = {3 : (0, -30 - 20), 4 : (0, -55 - 25), 5 : (0, -80 - 35)}
        buildingOffsets = {3 : (0, 10), 4 : (0, 0), 5 : (0, 15)}
        for t in teammate:
            self.images["Building", 1, t] = resource1
            self.images["Building", 2, t] = resource2

            for s in sides:
                pathBuilder = buildingsDir
                pathBuilder = pathBuilder.child(sides[s])
                pathBuilder = pathBuilder.child("%s_buildings" % (sides[s]))
                pathBuilder = pathBuilder.child("%s%s.png" % (sides[s], teammate[t]))
                self.images["Building", s, t] = Image(pathBuilder, buildingOffsets[s])

                pathBuilder = buildingsDir
                pathBuilder = pathBuilder.child(sides[s])
                pathBuilder = pathBuilder.child("%s_zones" % (sides[s]))
                pathBuilder = pathBuilder.child("%s_zone%s.png" % (sides[s], teammate[t]))
                self.images["Building Zone", s, t] = Image(pathBuilder)
                
                
                pathBuilder = buildingsDir
                pathBuilder = pathBuilder.child(sides[s])
                pathBuilder = pathBuilder.child("%s_armor%s" % (sides[s], teammate[t]))
                
                
                for resources in range(0, s + 1):
                    armorPath = pathBuilder.child("%s_armor%s%02d.png" % (sides[s], teammate[t], resources))
                    self.images["BuildingHealth", t, s, resources] = Image(armorPath, healthOffsets[s])

        self.images["TrapExplosion"] = Animation(dir.child("effects").child("explosion").child("explosion%04d.png"))
        self.images["building upgraded"] = Animation(dir.child("effects").child("build_effect").child("build_effect%04d.png"))
        self.images["BuildingAttacked"] = Animation(dir.child("effects").child("building_attacked").child("building_attacked%04d.png"))

    def _initArmorImages(self, dir):
        armorDir = dir.child("players").child("armor")
        sides = {3 : "tri", 4 : "sqr", 5 : "pent", 6 : "hex"}
        for i in sides:
            for j in range(1, i + 1):
                armorPath = armorDir.child("%s_armor" % (sides[i])).child("%s_armor%02d.png" % (sides[i], j))
                self.images["Armor", i, j] = Image(armorPath)

    def _addFlatlandAnimation(self, imageDirectory, action):
        # {imageDirectory}/{action}/flatland_{action}XXXX.png
        dir = imageDirectory.child(action)
        self.images[action] = Animation(dir.child("flatland_" + action + "%04d.png"))

    def load(self):
        for a in self.images:
            #print(str(a))
            self.images[a].load()
        self.images["Enemy",1].start(12);
        self.images["Enemy",2].start(12);
