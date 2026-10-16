import pygame
import snake as snk

TAM = 10
TICK_BASE = 10  # velocidad base
TICK_MAX = 40   # velocidad máxima


def get_tick():
    # Aumenta la velocidad según las manzanas comidas
    return min(TICK_BASE + snk.manzanas_comidas * 2, TICK_MAX)


def main():
    pygame.init()
    snk.init()
    ancho = snk.cols * TAM
    alto = snk.filas * TAM
    window = pygame.display.set_mode((ancho, alto))
    pygame.display.set_caption("Snake")
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
                # Reiniciar con R cuando la serpiente está muerta
                elif keys[pygame.K_r] and not snk.viva:
                    snk.init()

        window.fill((0, 0, 0))

        for f in range(snk.filas):
            for c in range(snk.cols):
                x = c * TAM
                y = f * TAM
                val = snk.matriz[f][c]
                if val == snk.MANZANA:
                    pygame.draw.rect(window, (255, 0, 0), (x, y, TAM, TAM))
                elif val == snk.MANZANA_DORADA:
                    pygame.draw.rect(window, (255, 215, 0), (x, y, TAM, TAM))
                elif val == snk.VENENO:
                    pygame.draw.rect(window, (0, 200, 0), (x, y, TAM, TAM))
                elif val > 0:
                    # Serpiente muerta = roja, viva = blanca
                    color = (255, 255, 255) if snk.viva else (200, 50, 50)
                    pygame.draw.rect(window, color, (x, y, TAM, TAM))

        snk.avanzar()
        pygame.display.update()
        clock.tick(get_tick())

    pygame.quit()


if __name__ == "__main__":
    main()
