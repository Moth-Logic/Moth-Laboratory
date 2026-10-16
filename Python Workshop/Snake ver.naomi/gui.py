import pygame
import snake as snk

TAM = 10
TICK = 20

def main():
    pygame.init()
    snk.init()
    ancho = snk.cols * TAM
    alto = snk.filas * TAM
    window = pygame.display.set_mode((ancho, alto))
    clock = pygame.time.Clock()
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    snk.cambiar_direccion("U")
                elif keys[pygame.K_DOWN]:
                    snk.cambiar_direccion("D")
                elif keys[pygame.K_LEFT]:
                    snk.cambiar_direccion("L")
                elif keys[pygame.K_RIGHT]:
                    snk.cambiar_direccion("R")

        window.fill((0, 0, 0))

        for f in range(snk.filas):
            for c in range (snk.cols):
                x = c * TAM
                y = f * TAM
                if snk.matriz[f][c] == snk.MANZANA:
                    pygame.draw.rect((window), (255, 0, 0), (x, y, TAM, TAM))
                elif snk.matriz[f][c] > 0:
                    pygame.draw.rect((window), (255, 255, 255), (x, y, TAM, TAM))
        snk.avanzar()
        pygame.display.update()
        clock.tick(TICK)

    pygame.quit()

if __name__ == "__main__":
    main()
