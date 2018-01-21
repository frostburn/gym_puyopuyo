#ifndef GYM_PUYOPUYO_BOTTOM_H_GUARD
#define GYM_PUYOPUYO_BOTTOM_H_GUARD

void bottom_render(puyos_t *floor, int num_colors);

int bottom_handle_gravity(puyos_t *floor, int num_colors);

puyos_t bottom_clear_groups(puyos_t *floor, int num_colors);

int bottom_resolve(puyos_t *floor, int num_layers, int has_garbage);

char* bottom_encode(puyos_t *floor, int num_colors);

bitset_t bottom_valid_moves(puyos_t *floor, int num_colors);

void make_move(puyos_t *floor, int action, int color_a, int color_b);

void mirror(puyos_t *floor, int num_colors);

double bottom_tree_search(puyos_t*, int, int, bitset_t, int*, int, int, double, puyos_t*);

#endif /* !GYM_PUYOPUYO_BOTTOM_H_GUARD */
