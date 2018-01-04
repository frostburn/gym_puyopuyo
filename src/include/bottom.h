#ifndef GYM_PUYOPUYO_BOTTOM_H_GUARD
#define GYM_PUYOPUYO_BOTTOM_H_GUARD

void bottom_render(puyos_t *floor, int num_colors);

int bottom_handle_gravity(puyos_t *floor, int num_colors);

int bottom_clear_groups(puyos_t *floor, int num_colors);

int bottom_resolve(puyos_t *floor, int num_colors);

char* bottom_encode(puyos_t *floor, int num_colors);

bitset_t bottom_valid_moves(puyos_t *floor, int num_colors);

#endif /* !GYM_PUYOPUYO_BOTTOM_H_GUARD */
