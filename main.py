import pygame
import pytmx
import pyscroll
from dataclasses import dataclass


BLANC = [255, 255, 255]
NOIR = [0, 0, 0]
BLEU_NUIT = [25, 25, 112]


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # charger la sprite sheet
        self.sprite_sheet = pygame.image.load("perso/perso.png").convert()
        self.image = self.get_image(0, 0) # image du perso par défaut
        self.rect = self.image.get_rect()
        self.position = [x,y]
        # dictionnaire qui stocke selon la direction(UP, DOWN...) toute les images de la sprite sheet
        self.images = { 'UP': self.get_images(self.image.get_width()*3),
                        'DOWN': self.get_images(self.image.get_width()),
                        'RIGHT': self.get_images(self.image.get_width()*2),
                        'LEFT': self.get_images(0) }
        self.frame = 0
        self.next_frame = 0
        self.vitesse = 3
        self.feet = pygame.Rect(0, 0, self.image.get_width() * 0.5, 15) # rect servant pour les collisionsdu perso
        self.old_position = self.position.copy()


    def get_image(self, x, y):
        """ permet de récupérer une image dans la sprite sheet selon sa position x et y, puis de la renvoyer """
        self.image = pygame.Surface([32, 32])
        self.image.set_colorkey(NOIR)
        self.image.blit(self.sprite_sheet, (0, 0), (x, y, self.image.get_width(), self.image.get_height()))
        return self.image


    def get_images(self, y):
        """ permet de récupérer les images d'une ligne de la sprite sheet selon l'ordonnée donnée en argument, puis de renvoyer la liste des images """
        images = []

        for i in range(0,4):
            x = i*self.image.get_width()
            image = self.get_image(x, y)
            images.append(image)
        return images


    def animation_deplacement(self, direction):
        """ selon sa direction, l'animation du déplacement va s'effectuer et sera ralentie """

        self.image = self.images[direction][self.frame]
        self.image.set_colorkey(NOIR)
        self.next_frame += self.vitesse * 6

        if self.next_frame >= 200:

            self.frame = (self.frame + 1) %  4
            self.next_frame = 0


    def update(self):
        """ permet d'actualiser la position du rect du perso (plus au topleft de l'écran), et du rect feet (en bas du rect du perso) """
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom


    def stop(self):
        """ c'est comme la fonction update sauf que cette fois la position du perso = son ancienne position, il va donc s'arrêter """
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom


    def deplacement_perso(self):
        """ possibilité de se déplacer en restant appuyé sur une flèche directionnelle + animation du perso selon sa direction """

        pressed = pygame.key.get_pressed() # lorsqu'une touche du clavier est enclenchée

        if pressed[pygame.K_RIGHT]:
            self.position[0] += self.vitesse
            self.animation_deplacement('RIGHT')

        elif pressed[pygame.K_LEFT]:
            self.position[0] -= self.vitesse
            self.animation_deplacement('LEFT')

        elif pressed[pygame.K_UP]:
            self.position[1] -= self.vitesse
            self.animation_deplacement('UP')

        elif pressed[pygame.K_DOWN]:
            self.position[1] += self.vitesse
            self.animation_deplacement('DOWN')



##-----------------------------------------------------------------------------------------------



class Dragon(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        # charge la sprite sheet du dragon
        self.dragon_sprite_sheet = pygame.image.load("images/dragon_sprite_sheet.png").convert_alpha()
        width = 140
        height = 120
        # récupère dans l'ordre toutes les images de la sprite sheet
        self.dragonSprite = [self.dragon_sprite_sheet.subsurface(width*(x%5), height*(x//5), width, height)for x in range(0,30)]
        self.frame = 0
        self.next_frame = 0


    def animation_dragon(self):
        """ permet une animation continue du dragon au ralenti (pas 60 FPS, mais 12 FPS) """
        self.dragon = self.dragonSprite[self.frame]
        self.dragon.set_colorkey(NOIR)
        self.next_frame += 20

        if self.next_frame >= 100:

            self.frame = (self.frame + 1) %  30
            self.next_frame = 0



##---------------------------------------------------------------------------------------------




@dataclass
class Portal:

    # 4 arguments qui vont permettre de:
    from_world: str    # définir le monde d'où vient le joueur
    origin_point: str  # définir le passage par lequel il va switcher de monde
    target_world: str  # définir le monde où il veut passer
    player_spawn: str  # définir le point de spawn du joueur



@dataclass
class Map:

    # 5 caractéristiques d'une map / d'un monde:
    nom: str                        # le nom
    obstacles: list[pygame.Rect]    # les obstacles
    group: pyscroll.PyscrollGroup   # le groupe
    tmx_data: pytmx.TiledMap        # le tmx_data
    portals: list[Portal]           # les portails



class MapManager:

    def __init__(self, ecran, player):

        self.maps = dict()
        self.ecran = ecran
        self.player = player
        self.monde = "map"

        # permet de passer de la carte à une des maisons
        self.register_map("map", portals=[
            Portal(from_world="map", origin_point="maison_entree", target_world="house", player_spawn="joueur_house"),
            Portal(from_world="map", origin_point="maison_entree2", target_world="house2", player_spawn="joueur_house2")])

        # permet de passer de la maison n°1 à la map ou à son étage supérieur
        self.register_map("house", portals=[
            Portal(from_world="house", origin_point="maison_sortie", target_world="map", player_spawn="joueur_sortie_house"),
            Portal(from_world="house", origin_point="maison_etage", target_world="house_etage", player_spawn="joueur_etage")])

        # permet de passer de l'étage de la maison n°1 au RDC
        self.register_map("house_etage", portals=[
            Portal(from_world="house_etage", origin_point="maison_floor", target_world="house", player_spawn="joueur_floor")])

        # permet de passer de la maison n°2 à la map
        self.register_map("house2", portals=[
            Portal(from_world="house2", origin_point="maison_sortie", target_world="map", player_spawn="joueur_sortie_house2")])

        # place le joueur au point "spawn_joueur"
        self.spawn_player("spawn_joueur")


    def check_collisions(self):
        """ récupère les infos de l'origin_point pour que, si le joueur rentre en collison avec, il puisse changer de monde. Et vérification des collisions avec les obstacles """

        # si le from_world de la classe Portal est le même que le monde, on définit l'origin_point qui est le rect d'accès à un autre monde
        for portal in self.get_map().portals:
            if portal.from_world == self.monde:
                point = self.get_object(portal.origin_point)
                rect = pygame.Rect(point.x, point.y, point.width, point.height)

                # si les pieds du joueur rentrent en collision avec l'origin_point, le monde devient le target_world, et le joueur apparaît à l'objet player_spawn placé sur Tiled
                if self.player.feet.colliderect(rect):
                    self.monde = portal.target_world
                    copy_portal = portal
                    self.spawn_player(copy_portal.player_spawn)

        # si les pieds du joueur rentre en collision avec la liste d'obstacles, il conserve la position d'avant avoir toucher un obstacle
        for sprite in self.get_group().sprites():
            if sprite.feet.collidelist(self.get_obstacles()) > -1:
                sprite.stop()


    def spawn_player(self, nom):
        """ permet de définir le point de spawn du joueur sur Tiled en donnant le nom de l'objet """
        point = self.get_object(nom)
        self.player.position[0] = point.x
        self.player.position[1] = point.y


    def register_map(self, nom, portals=[]):
        """ permet de charger la map selon son nom, et de charger la liste des portails """
        # charger une map
        tmx_data = pytmx.load_pygame(f"map/{nom}.tmx")
        map_data = pyscroll.TiledMapData(tmx_data)
        map_layer = pyscroll.BufferedRenderer(map_data, self.ecran.get_size(), zoom = 1.5)

        # liste de Rectangles de collisions: obstacles
        obstacles = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                obstacles.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # définir un groupe de calques
        group = pyscroll.PyscrollGroup(map_layer = map_layer, default_layer = 4)
        group.add(self.player)

        # instancier la classe Map selon le nom d'une map, chaque map possède son nom, ses obstacles, son groupe, ses données tmx, ses portails, ses PNJ...
        self.maps[nom] = Map(nom, obstacles, group, tmx_data, portals)


    def get_map(self):
        """ renvoie le dictionnaire maps avec le nom du monde dans lequel on se trouve """
        return self.maps[self.monde]

    def get_group(self):
        """ renvoie le groupe de calques qui constitue la map """
        return self.get_map().group

    def get_obstacles(self):
        """ renvoie les obstacles selon la map actuelle """
        return self.get_map().obstacles

    def get_object(self, nom):
        """ renvoie le nom d'un objet qui constitue la map actuelle """
        return self.get_map().tmx_data.get_object_by_name(nom)

    def draw(self):
        """ permet de dessiner le groupe de calques sur l'écran """
        self.get_group().draw(self.ecran)

    def center(self):
        """ permet de centrer le groupe sur le joueur"""
        self.get_group().center(self.player.rect.center)

    def update(self):
        """ actualise le groupe et vérifie les collisions d'obstacles ou de portails """
        self.get_group().update()
        self.check_collisions()



##---------------------------------------------------------------------------------------------




class Jeu:

    def __init__(self):

        # création de la surface d'affichage + du nom du jeu + de son icône
        self.ecran = pygame.display.set_mode((600, 600))
        self.ecran_rect = self.ecran.get_rect()
        pygame.display.set_caption("Pokemon DragonFly")
        pygame.display.set_icon(pygame.image.load("images/icone_jeu.png").convert())


        # on charge toutes les images
        fond_invent = pygame.image.load("images/fond_inventaire.jpg").convert() # Fond de l'inventaire
        self.fond_invent = pygame.transform.scale(fond_invent, (self.ecran.get_size()))

        icone_tab = pygame.image.load("images/tab.png").convert_alpha() # Touche TAB
        self.icone_tab = pygame.transform.scale(icone_tab, (80,50))

        icone_entrer = pygame.image.load("images/boutonEntrer.png").convert_alpha() # Touche ENTER
        self.icone_entrer = pygame.transform.scale(icone_entrer, (190,55))

        img_acc = pygame.image.load("images/start screen.png").convert() # Image de l'accueil
        self.img_acc = pygame.transform.scale(img_acc, (self.ecran.get_size()))

        icone_sac = pygame.image.load("images/sac.png").convert_alpha() # Sac
        self.icone_sac = pygame.transform.scale(icone_sac, (50,50))

        icone_esc = pygame.image.load("images/bouton_esc.png").convert_alpha() # Touche ECHAP
        self.icone_esc = pygame.transform.scale(icone_esc, (50,50))

        # on charge le texte d'accueil + son rect situé au centre de l'écran
        police = pygame.font.Font(None, 40)
        self.texte = police.render('Appuyez sur ENTER',True, BLEU_NUIT)
        self.texte_rect = self.texte.get_rect()
        self.texte_rect.center = self.ecran_rect.center
        self.texte_ajout_rectangle = pygame.Rect(self.texte_rect[0]-3, self.texte_rect[1]-3, 290, 33)

        # instance de classes
        self.player = Player(0,0)
        self.dragon = Dragon()
        self.map_manager = MapManager(self.ecran, self.player)


    def running(self):
        """ c'est la boucle du jeu avec toutes les fonctions, toutes les images à afficher... """
        clock = pygame.time.Clock()

        running = True
        ecran_accueil = True
        inventaire = False

        while running:

            # on peut fermer la fenêtre du jeu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Ecran d'accueil
            if ecran_accueil == True:

                # passer sur la map --> ENTER
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        ecran_accueil = False

            # Map
            else :

                # fonctions de la map
                if inventaire == False:

                    self.player.old_position = self.player.position.copy() # récupère l'ancienne position du perso
                    self.player.deplacement_perso() # déplace et anime le perso
                    self.map_manager.update() # actualise le groupe, et les collisions d'obstacles ou de portails
                    self.map_manager.center() # centre le perso et la map

                    # inventaire --> TAB
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                            inventaire = True

                # Inventaire
                if inventaire == True:

                    self.dragon.animation_dragon() # anime en continu le dragon dans l'inventaire

                    # fermer l'invnetaire --> ECHAP
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            inventaire = False


            # si écran d'accueil, on affiche les images de l'accueil
            if ecran_accueil == True:

                self.ecran.blit(self.img_acc,(0,0))
                self.ecran.blit(self.icone_entrer,(self.ecran.get_width() - 195 ,self.ecran.get_height() - 60))
                pygame.draw.rect(self.ecran, BLEU_NUIT, self.texte_ajout_rectangle, 2)
                self.ecran.blit(self.texte, self.texte_rect)

            # autrement, on affiche les images...
            else:

                # ... de l'inventaire
                if inventaire == True:

                    self.ecran.blit(self.fond_invent,(0,0))
                    self.ecran.blit(self.icone_esc,(self.ecran.get_width() - 55 ,self.ecran.get_height() - 55))
                    self.ecran.blit(self.dragon.dragon, (300, 200))

                # ... de la map
                else:

                    self.map_manager.draw() # dessine le groupe
                    self.ecran.blit(self.icone_sac,(self.ecran.get_width() - 130 ,self.ecran.get_height() - 50))
                    self.ecran.blit(self.icone_tab,(self.ecran.get_width() - 90 ,self.ecran.get_height() - 50))


            pygame.display.flip() # actualise l'écran

            clock.tick(60) # La boucle tourne à 60 FPS

        pygame.quit()


# initialiser le jeu
if __name__ == '__main__':
    pygame.init()
    jeu = Jeu()
    jeu.running() # la boucle du jeu se lance
