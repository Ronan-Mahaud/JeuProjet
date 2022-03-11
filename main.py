import pygame, pytmx, pyscroll




class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # charger la sprite sheet
        self.sprite_sheet = pygame.image.load("perso/sprite sheet perso.png").convert()
        self.image = self.get_image(0, 0) # image du perso par défaut
        self.rect = self.image.get_rect()
        self.position = [x,y]
        # dictionnaire qui stocke selon la direction(UP, DOWN...) toute les images de la sprite sheet
        self.images = { 'UP': self.get_images(36*3),
                        'DOWN': self.get_images(0),
                        'RIGHT': self.get_images(36),
                        'LEFT': self.get_images(36*2) }
        self.frame = 0
        self.next_frame = 0
        self.vitesse = 3
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 15) # rect servant pour les collisionsdu perso
        self.old_position = self.position.copy()
        

    def get_image(self, x, y):
        """ permet de récupérer une image dans la sprite sheet selon sa position x et y, puis de la renvoyer """
        self.image = pygame.Surface([36, 36])
        self.image.set_colorkey([255,255,255])
        self.image.blit(self.sprite_sheet, (0, 0), (x, y, self.image.get_width(), self.image.get_height()))
        return self.image


    def get_images(self, y):
        """ permet de récupérer les images d'une ligne de la sprite sheet selon l'ordonnée donnée en argument, puis de renvoyer la liste des images """
        images = []

        for i in range(0,4):
            x = i*36
            image = self.get_image(x, y)
            images.append(image)
        return images


    def animation_deplacement(self, direction):
        """ selon sa direction, l'animation du déplacement va s'effectuer et sera ralentie """

        self.image = self.images[direction][self.frame]
        self.image.set_colorkey([255,255,255])
        self.next_frame += self.vitesse * 6

        if self.next_frame >= 200:

            self.frame = (self.frame + 1) %  4
            self.next_frame = 0


    def update(self):
        """ permet d'actualiser la position du rect du perso (plus au topleft de l'écran), et du rect feet (en bas du rect du perso) """
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom
        
        
    def stop(self):
        """ c'est comme la fonction update sauf que cette fois la position du perso = son ancienne position, il va donc (normalement) s'arrêter"""
        self.position = self.old_position.copy()
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
        self.frame = 0
        self.next_frame = 0
        self.dragonSprite = [self.dragon_sprite_sheet.subsurface(140*(x%5), 120*(x//5), 140, 120)for x in range(0,30)]


    def animation_dragon(self):
        """ permet une animation continue du dragon au ralenti (pas 60 FPS, mais 12 FPS) """
        self.dragon = self.dragonSprite[self.frame]
        self.dragon.set_colorkey((0,0,0))
        self.next_frame += 20

        if self.next_frame >= 100:

            self.frame = (self.frame + 1) %  30
            self.next_frame = 0



##-------------------------------------------------------------------------------------------




class Jeu:

    def __init__(self):
        global tmx_data

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
        self.BLEU_NUIT = (25,25,112)
        police = pygame.font.Font(None, 40)
        self.texte = police.render('Appuyez sur ENTER',True, self.BLEU_NUIT)
        self.texte_rect = self.texte.get_rect()
        self.texte_rect.center = self.ecran_rect.center
        self.texte_ajout_rectangle = pygame.Rect(self.texte_rect[0]-3, self.texte_rect[1]-3, 290, 33)


        # instance de classes
        self.player = Player(400, 400)
        self.dragon = Dragon()

        self.charger_monde("map", 200, 500)

        # définir l'entrée de la maison
        self.entree_maison = self.tmx_data.get_object_by_name('maison_entree')
        self.entree_maison_rect = pygame.Rect(self.entree_maison.x, self.entree_maison.y, self.entree_maison.width, self.entree_maison.height)


    def collisions(self):
        """ fait une liste de rectangles /obstacles/ avec toutes leurs valeurs (x, y, largeur, hauteur)"""
        self.obstacles = []
        
        for obj in self.tmx_data.objects:
            if obj.type == "collision":
                self.obstacles.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

                
    def charger_monde(self, nom, pos_x, pos_y):
        """ permet de charger un monde selon son nom et définir la position du perso selon les données données en argument """
        # charger la map
        self.tmx_data = pytmx.load_pygame(f"map/{nom}.tmx")
        map_data = pyscroll.TiledMapData(self.tmx_data)
        map_layer = pyscroll.BufferedRenderer(map_data, self.ecran.get_size(), zoom = 1.5)

        # définir un groupe de calques
        self.group = pyscroll.PyscrollGroup(map_layer = map_layer, default_layer = 4)
        self.group.add(self.player)

        self.collisions()

        self.player.position[0] = int(pos_x)
        self.player.position[1] = int(pos_y)


    def switch_house(self):
        """ permet de changer de monde, on passe du monde 'map' au monde 'house' + on peut sortir de la maison """
        self.charger_monde("house", 75, 320)

        # définir le point de sortie de la maison
        self.sortie_maison = self.tmx_data.get_object_by_name('maison_sortie')
        self.entree_maison_rect = pygame.Rect(self.sortie_maison.x, self.sortie_maison.y, self.sortie_maison.width, self.sortie_maison.height)


    def switch_map(self):
        """ permet de changer de monde, on passe du monde 'house' au monde 'map' + on peut rentrer dans la maison """
        self.charger_monde("map", 150, 200)

        # définir le point d'entrée de la maison
        self.entree_maison = self.tmx_data.get_object_by_name('maison_entree')
        self.entree_maison_rect = pygame.Rect(self.entree_maison.x, self.entree_maison.y, self.entree_maison.width, self.entree_maison.height)


    def update(self):
        """ gère et actualise le group, les changements de map, et les collisions"""
        self.group.update()

        if self.player.feet.colliderect(self.entree_maison_rect):
            self.switch_house()

        if self.player.feet.colliderect(self.entree_maison_rect):
            self.switch_map()

        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.obstacles)>-1:
                sprite.stop()


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
                    self.update() # actualise la position du perso, les collisions, les changements de map
                    self.group.center(self.player.rect.center) # centre le perso et la map
                    self.player.deplacement_perso() # déplace et anime le perso

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
                pygame.draw.rect(self.ecran, self.BLEU_NUIT, self.texte_ajout_rectangle, 2)
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

                    self.group.draw(self.ecran)
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
