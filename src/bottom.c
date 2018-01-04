#include <stdio.h>
#include <stdlib.h>

#include "include/bitboard.h"
#include "include/bottom.h"

void bottom_render(puyos_t *floor, int num_colors) {
  puyos_t p = 1;
  for (int i = 0; i < HEIGHT; ++i) {
    for (int j = 0; j < WIDTH; ++j) {
      int empty = 1;
      for (int k = 0; k < num_colors; ++k) {
        if (floor[k] & p) {
          printf("%d ", k);
          empty = 0;
        }
      }
      if (empty) {
        printf(". ");
      }
      p <<= 1;
    }
    printf("\n");
  }
}

int bottom_handle_gravity(puyos_t *floor, int num_colors) {
  puyos_t all;
  all = 0;
  for (int j = 0; j < num_colors; ++j) {
    all |= floor[j];
  }

  int iterations = 0;
  puyos_t temp;
  do {
    temp = all;
    puyos_t bellow, falling;
    bellow = (all >> V_SHIFT) | BOTTOM;
    all = 0;
    for (int i = 0; i < num_colors; ++i) {
      falling = floor[i] & ~bellow;
      floor[i] = (falling << V_SHIFT) | (floor[i] & bellow);
      all |= floor[i];
    }
    ++iterations;
  } while (temp != all);

  return iterations;
}

int bottom_clear_groups(puyos_t *floor, int num_colors) {
  int num_cleared = 0;
  for (int i = 0; i < num_colors; ++i) {
    puyos_t bottom = floor[i];
    for (int j = WIDTH * HEIGHT - 2; j >= 0; j -= 2) {
      puyos_t bottom_group = 3ULL << j;
      bottom_group = flood(bottom_group, bottom);
      bottom ^= bottom_group;
      int group_size = popcount(bottom_group);
      if (group_size >= CLEAR_THRESHOLD) {
        floor[i] ^= bottom_group;
        num_cleared += group_size;
      }
      if (!bottom) {
        break;
      }
    }
  }
  return num_cleared;
}

int bottom_resolve(puyos_t *floor, int num_colors) {
  int chain = -1;
  while(1) {
    ++chain;
    int iterations = bottom_handle_gravity(floor, num_colors);
    if (iterations == 1 && chain > 0) {
      break;
    }
    if (!bottom_clear_groups(floor, num_colors)) {
      break;
    }
  }
  return chain;
}

char* bottom_encode(puyos_t *floor, int num_colors) {
  char* data = malloc(num_colors * WIDTH * HEIGHT * sizeof(char));
  puyos_t p = 1;
  for (int j = 0; j < WIDTH * HEIGHT; ++j) {
    for (int i = 0; i < num_colors; ++i) {
      data[j + i * WIDTH * HEIGHT] = !!(p & floor[i]);
    }
    p <<= 1;
  }
  return data;
}

bitset_t bottom_valid_moves(puyos_t *floor, int num_colors) {
  puyos_t all = 0;
  for (int i = 0; i < num_colors; ++i) {
    all |= floor[i];
  }

  bitset_t result = 0;
  bitset_t m = 1;

  puyos_t piece = 3;
  for (int i = 0; i < WIDTH - 1; ++i) {
    if (!(piece & all)) {
      result |= m;
    }
    piece <<= 1;
    m <<= 1;
  }

  piece = 1 | (1 << V_SHIFT);
  for (int i = 0; i < WIDTH; ++i) {
    if (!(piece & all)) {
      result |= m;
    }
    piece <<= 1;
    m <<= 1;
  }

  return result;
}
