class Entity(object):
    def __init__(self):
        pass

    def __eq__(self, other):
        return False


class ColoredEntity(Entity):
    @property
    def sprite_color(self):
        """Shuffle colors to be consistent with ansi rendering"""
        if self.color == 2:
            return 3
        elif self.color == 3:
            return 2
        return self.color


class Puyo(ColoredEntity):
    def __init__(self, color):
        self.color = color
        self.falling = False


    def __eq__(self, other):
        if not isinstance(other, Puyo):
            return False
        if self.falling or other.falling:
            return False
        return self.color == other.color

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.color)


class Pop(ColoredEntity):
    MAX_AGE = 2

    def __init__(self, color):
        self.color = color
        self.age = 0

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.color)


class Garbage(Entity):
    pass


class Ground(Entity):
    pass


class AnimationState(object):
    def __init__(self, state):
        self.state = state
        self.infer_entities()

    @property
    def width(self):
        return self.state.width

    @property
    def height(self):
        # TODO: Figure out gravity for tsu
        return self.state.field.HEIGHT

    @property
    def tsu_rules(self):
        return self.state.tsu_rules

    @property
    def deals(self):
        result = []
        for deal in self.state.deals:
            result.append((Puyo(deal[0]), Puyo(deal[1])))
        return result

    def infer_entities(self):
        self.entities = [self.infer_entity(puyo) for puyo in self.state.to_list()]

    def infer_entity(self, color):
        if color is None:
            return None
        if color == self.state.num_colors:
            return Garbage()
        return Puyo(color)

    def __getitem__(self, xy):
        x, y = xy
        if y >= self.height:
            return Ground()
        if y < 0 or x < 0 or x >= self.width:
            return None
        return self.entities[x + y * self.width]

    def __setitem__(self, xy, entity):
        x, y = xy
        self.entities[x + y * self.width] = entity

    def step_pops(self):
        for i in range(len(self.entities)):
            entity = self.entities[i]
            if isinstance(entity, Pop):
                entity.age += 1
                if entity.age >= entity.MAX_AGE:
                    self.entities[i] = None

    def _resolve_cycle(self):
        while self.step_gravity():
            yield self

        self.state.field.handle_gravity()

        old_field = self.state.to_list()
        score = self.state.field.clear_groups(1)
        if score:
            new_field = self.state.to_list()
            for i in range(len(new_field)):
                new = new_field[i]
                old = old_field[i]
                if old is not None and new != old:
                    self.entities[i] = Pop(old)
            yield self
            self.step_pops()
            yield self
            self.step_pops()
            yield self
            self.infer_entities()

    def resolve(self):
        yield self

        changed = True
        while changed:
            changed = False
            for frame in self._resolve_cycle():
                changed = True
                yield frame

        if self.tsu_rules:
            score, chain = self.state.field.resolve()
            assert (not score)

        self.infer_entities()

    def step_gravity(self):
        changed = False
        for i, entity in reversed(list(enumerate(self.entities[:]))):
            if not entity:
                continue
            y, x = divmod(i, self.width)
            if self[x, y + 1] is None:
                self[x, y + 1] = entity
                self[x, y] = None
                entity.falling = True
                changed = True
            else:
                entity.falling = False
        return changed

    def to_list(self):
        result = []
        for entity in self.entities:
            if isinstance(entity, Puyo):
                result.append(entity.color)
            else:
                result.append(None)
        return result
