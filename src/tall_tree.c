#include <stdlib.h>
#include <string.h>

#include <stdio.h>

#include "bitboard.h"
#include "bottom.h"
#include "tall.h"

#define GAMMA (0.95)
#define DEATH_VALUE (-10000)

int tall_group_heuristic(puyos_t *top, puyos_t *bottom, int num_colors) {
    int score = 0;
    for (int i = 0; i < num_colors; ++i) {
        puyos_t layer[2] = {top[i], bottom[i]};
        for (int k = 0; k < NUM_FLOORS; ++k) {
            for (int j = 0; j < WIDTH * HEIGHT; j += 2) {
                puyos_t group[2] = {0, 0};
                group[k] = 3ULL << j;
                flood_2(group, layer);
                layer[0] ^= group[0];
                layer[1] ^= group[1];
                int size = popcount_2(group);
                score += size * size;
            }
        }
    }
    return score;
}

double tall_tree_search_single(
    puyos_t *floors,
    int num_layers,
    int width,
    int tsu_rules,
    int has_garbage,
    bitset_t action_mask,
    int *colors,
    int num_deals,
    int depth,
    double factor,
    puyos_t *child_buffer
) {
    bitset_t valid = tall_valid_moves(floors, num_layers, width, tsu_rules);
    valid |= valid << (NUM_ACTIONS / 2);
    valid &= action_mask;

    if (!valid) {
        return DEATH_VALUE;
    }

    double score = DEATH_VALUE;
    puyos_t *child = child_buffer;

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

        memcpy(child, floors, sizeof(puyos_t) * num_layers * NUM_FLOORS);
        make_move(child, i, colors[0], colors[1]);

        int dummy;
        double move_score = tall_resolve(child, num_layers, tsu_rules, has_garbage, &dummy);

        double tree_score = tall_tree_search(
            child,
            num_layers,
            width,
            tsu_rules,
            has_garbage,
            action_mask,
            colors + 2,
            num_deals - 1,
            depth - 1,
            factor,
            child_buffer + num_layers * NUM_FLOORS
        );

        double child_score = move_score + GAMMA * tree_score;
        if (child_score > score) {
            score = child_score;
        }
    }
    return score;
}

double tall_tree_search(
    puyos_t *floors,
    int num_layers,
    int width,
    int tsu_rules,
    int has_garbage,
    bitset_t action_mask,
    int *colors,
    int num_deals,
    int depth,
    double factor,
    puyos_t *child_buffer
) {
    int num_colors = num_layers - has_garbage;

    if (depth <= 0) {
        return factor * tall_group_heuristic(floors, floors + num_layers, num_colors);
    }

    if (num_deals > 0) {
        // Deterministic search with the provided colors.
        return tall_tree_search_single(
            floors,
            num_layers,
            width,
            tsu_rules,
            has_garbage,
            action_mask,
            colors,
            num_deals - 1,
            depth,
            factor,
            child_buffer
        );
    } else {
        // Averaged search over all possible color combinations.
        double tree_score = 0;
        for (int c0 = 0; c0 < num_colors; ++c0) {
            colors[0] = c0;
            // Symmetry reduction
            for (int c1 = c0; c1 < num_colors; ++c1) {
                colors[1] = c1;
                double single_score = tall_tree_search_single(
                    floors,
                    num_layers,
                    width,
                    tsu_rules,
                    has_garbage,
                    action_mask,
                    colors,
                    0,
                    depth,
                    factor,
                    child_buffer
                );
                // Symmetry compensation
                if (c1 == c0) {
                    tree_score += single_score;
                } else {
                    tree_score += 2 * single_score;
                }
            }
        }
        tree_score /= num_colors * num_colors;
        return tree_score;
    }
}
