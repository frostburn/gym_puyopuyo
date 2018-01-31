#include <stdio.h>
#include <stdlib.h>

#include "bitboard.h"
#include "bottom.h"

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

puyos_t bottom_clear_groups(puyos_t *floor, int num_colors) {
  puyos_t cleared = 0;
  for (int i = 0; i < num_colors; ++i) {
    puyos_t bottom = floor[i];
    for (int j = WIDTH * HEIGHT - 2; j >= 0; j -= 2) {
      puyos_t bottom_group = 3ULL << j;
      bottom_group = flood(bottom_group, bottom);
      bottom ^= bottom_group;
      int group_size = popcount(bottom_group);
      if (group_size >= CLEAR_THRESHOLD) {
        floor[i] ^= bottom_group;
        cleared |= bottom_group;
      }
      if (!bottom) {
        break;
      }
    }
  }
  return cleared;
}

int bottom_resolve(puyos_t *floor, int num_layers, int has_garbage) {
  int chain = -1;
  while(1) {
    ++chain;
    int iterations = bottom_handle_gravity(floor, num_layers);
    if (iterations == 1 && chain > 0) {
      break;
    }
    puyos_t cleared = bottom_clear_groups(floor, num_layers - has_garbage);
    if (!cleared) {
      break;
    } else if (has_garbage) {
      floor[num_layers - 1] &= ~cross(cleared);
    }
  }
  return chain;
}

int bottom_clear_groups_and_garbage(puyos_t *floor, int num_layers, int has_garbage) {
  puyos_t cleared = bottom_clear_groups(floor, num_layers - has_garbage);
  if (cleared && has_garbage) {
    floor[num_layers - 1] &= ~cross(cleared);
  }
  return !!cleared;
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

  bitset_t result = TOP & ~all;
  result &= result >> 1;
  result |= (TOP & ~(all | (all >> V_SHIFT))) << (WIDTH - 1);
  return result;
}

// This is valid for both bottom and tall fields due to the data layout
void make_move(puyos_t *floor, int action, int color_a, int color_b) {
  int x = action;
  int orientation = 0;
  if (x >= WIDTH - 1) {
    x -= WIDTH - 1;
    orientation = 1;
    if (x >= WIDTH) {
      x -= WIDTH;
      orientation = 2;
      if (x >= WIDTH - 1) {
        x -= WIDTH - 1;
        orientation = 3;
      }
    }
  }
  if (orientation == 0) {
    floor[color_a] |= 1ULL << x;
    floor[color_b] |= 1ULL << (x + 1);
  } else if (orientation == 1) {
    floor[color_a] |= 1ULL << x;
    floor[color_b] |= 1ULL << (x + V_SHIFT);
  } else if (orientation == 2) {
    floor[color_b] |= 1ULL << x;
    floor[color_a] |= 1ULL << (x + 1);
  } else {
    floor[color_b] |= 1ULL << x;
    floor[color_a] |= 1ULL << (x + V_SHIFT);
  }
}

void mirror(puyos_t *floor, int num_colors) {
  for (int i = 0; i < num_colors; ++i) {
    puyos_t puyos = floor[i];
    puyos = ((puyos & RIGHT_HALF) >> (WIDTH / 2)) | ((puyos << (WIDTH / 2)) & RIGHT_HALF);
    puyos = ((puyos & RIGHT_DELTA_1) >> (WIDTH / 4)) | ((puyos << (WIDTH / 4)) & RIGHT_DELTA_1);
    floor[i] = ((puyos & RIGHT_DELTA_2) >> 1) | ((puyos << 1) & RIGHT_DELTA_2);
  }
}
