#include <stdlib.h>
#include <string.h>

#include <stdio.h>

#include "bitboard.h"
#include "bottom.h"

#define GAMMA (0.95)
#define DEATH_VALUE (-10)

int bottom_group_heuristic(puyos_t *floor, int num_colors) {
    int score = 0;
    for (int i = 0; i < num_colors; ++i) {
        puyos_t layer = floor[i];
        for (int j = 0; j < WIDTH * HEIGHT; j += 2) {
            puyos_t group = flood(3ULL << j, layer);
            layer ^= group;
            int size = popcount(group);
            score += size * size;
        }
    }
    return score;
}

double bottom_tree_search(
    puyos_t *floor,
    int num_layers,
    int has_garbage,
    bitset_t action_mask,
    int *colors,
    int num_deals,
    int depth,
    double factor
) {
    int num_colors = num_layers - has_garbage;
    bitset_t valid = bottom_valid_moves(floor, num_layers);
    valid |= valid << (NUM_ACTIONS / 2);
    valid &= action_mask;

    if (!valid) {
        return DEATH_VALUE;
    }

    if (depth == 0) {
        return factor * bottom_group_heuristic(floor, num_colors);
    }

    double score = -1;
    puyos_t *child = malloc(sizeof(puyos_t) * num_layers);
    int *temp_colors = NULL;
    if (num_deals <= 1) {
        temp_colors = malloc(sizeof(int) * 2);
    }

    // Symmetry reduction
    int num_actions = NUM_ACTIONS;
    if (colors[0] == colors[1]) {
        num_actions /= 2;
    }

    for (int i = 0; i < num_actions; ++i) {
        bitset_t move = 1ULL << i;
        if (!(valid & move)) {
            continue;
        }

        memcpy(child, floor, sizeof(puyos_t) * num_layers);
        make_move(child, i, colors[0], colors[1]);

        double move_score = bottom_resolve(child, num_layers, has_garbage);
        move_score *= move_score;

        double tree_score;
        if (num_deals > 1) {
            // Deterministic search one ply deeper
            tree_score = bottom_tree_search(child, num_layers, has_garbage, action_mask, colors + 2, num_deals - 1, depth - 1, factor);
        } else {
            // Averaged search over all possible plys.
            tree_score = 0;
            for (int c0 = 0; c0 < num_colors; ++c0) {
                temp_colors[0] = c0;
                // Symmetry reduction
                for (int c1 = c0; c1 < num_colors; ++c1) {
                    temp_colors[1] = c1;
                    double some_score = bottom_tree_search(child, num_layers, has_garbage, action_mask, temp_colors, 0, depth - 1, factor);
                    // Symmetry compensation
                    if (c1 == c0) {
                        tree_score += some_score;
                    } else {
                        tree_score += 2 * some_score;
                    }
                }
            }
            tree_score /= num_colors * num_colors;
        }

        double child_score = move_score + GAMMA * tree_score;
        if (child_score > score) {
            score = child_score;
        }
    }
    free(child);
    free(temp_colors);
    return score;
}
