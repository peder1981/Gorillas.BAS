#!/usr/bin/env python3
"""
Gorilla 2.0: modern reinterpretation of QBASIC Gorillas.BAS using Pygame.
"""

import sys
import pygame


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Gorilla 2.0")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((135, 206, 235))  # sky blue background

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()