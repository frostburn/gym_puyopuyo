#include <stdio.h>
#include <stdlib.h>

#include "bitboard.h"
#include "bottom.h"
#include "tall.h"

const int COLOR_BONUS[MAX_COLOR_BONUS + 1] = {0, 0, 3, 6, 12, 24, 48};
const int GROUP_BONUS[MAX_GROUP_BONUS + 1] = {0, 2, 3, 4, 5, 6, 7, 10};
const int CHAIN_POWERS[MAX_CHAIN_POWER + 1] = {
    0, 8, 16, 32, 64, 96, 128, 160, 192, 224, 256, 288,
    320, 352, 384, 416, 448, 480, 512, 544, 576, 608, 640, 672
};

void tall_render(puyos_t *floors, int num_colors) {
  for (int l = 0; l < NUM_FLOORS; ++l) {
    puyos_t p = 1;
    for (int i = 0; i < HEIGHT; ++i) {
      for (int j = 0; j < WIDTH; ++j) {
        int empty = 1;
        for (int k = 0; k < num_colors; ++k) {
          if (floors[k + l * num_colors] & p) {
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
}

int tall_handle_gravity(puyos_t *floors, int num_colors) {
    puyos_t *top = floors;
    puyos_t *bottom = floors + num_colors;
    puyos_t all_top = 0;
    puyos_t all_bottom = 0;
    for (int j = 0; j < num_colors; ++j) {
        all_top |= top[j];
        all_bottom |= bottom[j];
    }

    int iterations = 0;
    puyos_t temp_top, temp_bottom;
    do {
        temp_top = all_top;
        temp_bottom = all_bottom;
        puyos_t bellow, falling;
        bellow = (all_bottom >> V_SHIFT) | BOTTOM;
        all_bottom = 0;
        for (int i = 0; i < num_colors; ++i) {
            falling = bottom[i] & ~bellow;
            bottom[i] = (falling << V_SHIFT) | (bottom[i] & bellow);
            all_bottom |= bottom[i];
        }

        bellow = (all_top >> V_SHIFT) | ((all_bottom & TOP) << TOP_TO_BOTTOM);
        all_top = 0;
        for (int i = 0; i < num_colors; ++i) {
            falling = top[i] & ~bellow;

            bottom[i] |= (falling & BOTTOM) >> TOP_TO_BOTTOM;

            top[i] = (falling << V_SHIFT) | (top[i] & bellow);
            all_top |= top[i];
        }
        ++iterations;
    } while (temp_top != all_top || temp_bottom != all_bottom);
    return iterations;
}

int tall_clear_groups(puyos_t *floors, int num_colors, int chain_number, int tsu_rules, puyos_t *cleared) {
    puyos_t *top = floors;
    puyos_t *bottom = floors + num_colors;
    int num_cleared = 0;
    int group_bonus = 0;
    bitset_t color_flags = 0;
    cleared[0] = 0;
    cleared[1] = 0;
    puyos_t life_block = FULL;
    int min_index = 0;
    if (tsu_rules) {
        life_block = LIFE_BLOCK;
        min_index = 4 * WIDTH;
    }
    for (int i = 0; i < num_colors; ++i) {
        puyos_t layer[2] = {top[i] & life_block, bottom[i]};

        for (int j = HEIGHT * WIDTH - 2; j >= min_index; j -= 2) {
            puyos_t top_group[2] = {3ULL << j, 0};
            flood_2(top_group, layer);
            layer[0] ^= top_group[0];
            layer[1] ^= top_group[1];
            int group_size = popcount_2(top_group);
            if (group_size >= CLEAR_THRESHOLD) {
                top[i] ^= top_group[0];
                bottom[i] ^= top_group[1];
                num_cleared += group_size;

                group_size -= CLEAR_THRESHOLD;
                if (group_size > MAX_GROUP_BONUS) {
                    group_size = MAX_GROUP_BONUS;
                }
                group_bonus += GROUP_BONUS[group_size];
                color_flags |= 1ULL << i;
                cleared[0] |= top_group[0];
                cleared[1] |= top_group[1];
            }
            if (!layer[0]) {
                break;
            }
        }
        puyos_t bottom_layer = bottom[i];
        for (int j = HEIGHT * WIDTH - 2; j >= 0; j -= 2) {
            puyos_t bottom_group = flood(3ULL << j, bottom_layer);
            if (!bottom_group) {
                continue;
            }
            bottom_layer ^= bottom_group;
            int group_size = popcount(bottom_group);
            if (group_size >= CLEAR_THRESHOLD) {
                bottom[i] ^= bottom_group;
                num_cleared += group_size;

                group_size -= CLEAR_THRESHOLD;
                if (group_size > MAX_GROUP_BONUS) {
                    group_size = MAX_GROUP_BONUS;
                }
                group_bonus += GROUP_BONUS[group_size];
                color_flags |= 1ULL << i;

                cleared[1] |= bottom_group;
            }
            if (!bottom_layer) {
                break;
            }
        }
    }
    int color_bonus = popcount(color_flags);
    if (color_bonus > MAX_COLOR_BONUS) {
        color_bonus = MAX_COLOR_BONUS;
    }
    color_bonus = COLOR_BONUS[color_bonus];
    if (chain_number > MAX_CHAIN_POWER) {
        chain_number = MAX_CHAIN_POWER;
    }
    int chain_power = CHAIN_POWERS[chain_number];
    int clear_bonus = chain_power + color_bonus + group_bonus;
    if (clear_bonus < 1) {
        clear_bonus = 1;
    } else if (clear_bonus > MAX_CLEAR_BONUS) {
        clear_bonus = MAX_CLEAR_BONUS;
    }
    return (10 * num_cleared) * clear_bonus;
}

void tall_kill_puyos(puyos_t *floors, int num_colors) {
    for (int i = 0; i < num_colors; ++i) {
        floors[i] &= SEMI_LIFE_BLOCK;
    }
}

int tall_resolve(puyos_t *floors, int num_colors, int tsu_rules, int *chain_out) {
    int chain = -1;
    int total_score = 0;
    while(1) {
        ++chain;
        int iterations = tall_handle_gravity(floors, num_colors);
        if (iterations == 1 && chain > 0) {
            break;
        }
        if (tsu_rules) {
            tall_kill_puyos(floors, num_colors);
        }
        puyos_t cleared[2];
        int score = tall_clear_groups(floors, num_colors, chain, tsu_rules, cleared);
        if (!score) {
            break;
        }
        total_score += score;
    }
    int all_clear_bonus = 0;
    if (total_score) {
        all_clear_bonus = 8500;
        for (int i = 0; i < num_colors; ++i) {
            if (floors[num_colors + i]) {
                all_clear_bonus = 0;
                break;
            }
        }
    }
    *chain_out = chain;
    return total_score + all_clear_bonus;
}

char* tall_encode(puyos_t *floors, int num_colors) {
  char* data = malloc(num_colors * NUM_FLOORS * WIDTH * HEIGHT * sizeof(char));
  int index = 0;
  for (int k = 0; k < NUM_FLOORS; ++k) {
      puyos_t p = 1;
      for (int j = 0; j < WIDTH * HEIGHT; ++j) {
        for (int i = 0; i < num_colors; ++i) {
          data[index + i * NUM_FLOORS * WIDTH * HEIGHT] = !!(p & floors[i + k * num_colors]);
        }
        index += 1;
        p <<= 1;
      }
  }
  return data;
}

bitset_t tall_valid_moves(puyos_t *floors, int num_colors, int tsu_rules) {
  if (!tsu_rules) {
    return bottom_valid_moves(floors, num_colors);
  }
  puyos_t all = 0;
  for (int i = 0; i < num_colors; ++i) {
    all |= floors[i];
  }
  all >>= 3 * V_SHIFT;

  bitset_t result = TOP & ~all;
  result |= result >> 1;
  result &= 0x7FULL;
  result |= (TOP & ~all) << (WIDTH - 1);

  return result;
}
