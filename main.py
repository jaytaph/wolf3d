import pygame as pg
import math

WINSIZE = [640, 400]

HSIZE = WINSIZE[1]
WSIZE = WINSIZE[0]
# Center of the screen
H2SIZE = HSIZE >> 1

MAPSIZE = [24, 24]

# Feature flags
TEXTURE_WALLS_ENABLED = True
TEXTURE_FLOORS_ENABLED = True
DISPLAY_HUD_MAP = False

MAP = """
XXXXXXXXXXXXXXXXXXXXXXXX
X                      X
X                      X
X          X           X
X          X           X
XXXXXXXXXXXX           X
X                      X
X        4444          X
X222222  4             X
X     2  4         XXXXX
X  1  2  4             X
X  1  2  4             X
X  1  2  4             X
X  1     4             X
X  1333334             X
X                      X
XXXXXXXX               X
X      X               X
X   X  X               X
X   X  X               X
X  XXXXX               X
X                      X
X                      X
XXXXXXXXXXXXXXXXXXXXXXXX
""".replace("\n", "")


MAP1 = """
X------XXXXXXXXXXXXXXXXX
X                      X
X                      X
X                      X
X                      X
X                      X
X                      X
X                      X
X            1         X
X           2          X
X          3           X
X         4            X
X                      X
X                      X
X                      X
X                      X
X                      X
X                      X
X                      X
X                      X
X                      X
X                      X
X                      X
X----------------------X
""".replace("\n", "")

class COLOR:
    black = (0, 0, 0)
    white = (0, 255, 255)
    gray = (180, 180, 180)
    green = (0, 200, 0)
    red = (200, 0, 0)
    blue = (0, 0, 200)
    purple = (200, 200, 0)
    ceil = (0x25, 0x56, 0x7B)
    floor = (0xBF, 0x82, 0x30)

class Player:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dir_x = dx
        self.dir_y = dy
        self.plane_x = 0
        self.plane_y = 1
        self.angle = 0


def get_tile_from_map(x, y):
    return MAP[y * MAPSIZE[0] + x]


def darken_color(c, divisor):
    return tuple(ci / divisor for ci in c)


def ray_cast(screen, player, textures):
    # Iterate each vertical line. Cast a ray and see what we hit
    for x in range(0, WINSIZE[0]-1):
        # calculate ray position and direction
        camera_x = 2 * x / WINSIZE[0] - 1
        ray_dir_x = player.dir_x + (player.plane_x * camera_x)
        ray_dir_y = player.dir_y + (player.plane_y * camera_x)

        # map_* is the tile which we currently reside in
        map_x = int(player.x)
        map_y = int(player.y)

        # Calculate the direction of our ray
        if ray_dir_y == 0:
            dist_delta_x = 0
        else:
            if ray_dir_x == 0:
                dist_delta_x = 1
            else:
                dist_delta_x = abs(1 / ray_dir_x)

        if ray_dir_x == 0:
            dist_delta_y = 0
        else:
            if ray_dir_y == 0:
                dist_delta_y = 1
            else:
                dist_delta_y = abs(1 / ray_dir_y)

        # Did we hit a wall?
        hit = 0
        # Which side of the wall did we hit (NE or SW)
        side = 0
        # Which tile did we hit
        tile = ''

        # Calculate step and initial side delta to get to the first edge of the map from our position
        if ray_dir_x < 0:
            step_x = -1
            side_distance_x = (player.x - map_x) * dist_delta_x
        else:
            step_x = 1
            side_distance_x = (map_x + 1.0 - player.x) * dist_delta_x
        if ray_dir_y < 0:
            step_y = -1
            side_distance_y = (player.y - map_y) * dist_delta_y
        else:
            step_y = 1
            side_distance_y = (map_y + 1.0 - player.y) * dist_delta_y

        # Cast the ray until we hit something
        while hit == 0:
            # Go to next tile
            if side_distance_x < side_distance_y:
                side_distance_x += dist_delta_x
                map_x += step_x
                side = 0
            else:
                side_distance_y += dist_delta_y
                map_y += step_y
                side = 1

            # Check if there is something on this tile
            tile = get_tile_from_map(map_x, map_y)
            if tile != ' ':
                hit = 1

        #
        if side == 0:
            perp_wall_distance = (map_x - player.x + (1 - step_x) / 2) / ray_dir_x
        else:
            perp_wall_distance = (map_y - player.y + (1 - step_y) / 2) / ray_dir_y

        # if perp_wall_distance == 0:
        #     continue

        # Calculate height of the wall, based on the distance
        if perp_wall_distance == 0:
            line_height = HSIZE
        else:
            line_height = int(HSIZE / perp_wall_distance)

        draw_start = int(0 - line_height / 2 + HSIZE / 2)
        if draw_start < 0:
            draw_start = 0
        draw_end = int(line_height / 2 + HSIZE / 2)
        if draw_end > HSIZE:
            draw_end = HSIZE - 1


        if TEXTURE_WALLS_ENABLED:
            texture = textures[tile]

            if side == 0:
                wall_x = player.y + perp_wall_distance * ray_dir_y
            else:
                wall_x = player.x + perp_wall_distance * ray_dir_x
            wall_x -= math.floor(wall_x)

            tex_x = int(wall_x * 64)
            if side == 0 and ray_dir_x > 0:
                tex_x = 64 - tex_x - 1
            if side == 1 and ray_dir_y < 0:
                tex_x = 64 - tex_x - 1

            step = 1.0 * 64 / line_height

            tex_pos = (draw_start - H2SIZE + line_height / 2) * step

            for y in range(draw_start, draw_end):
                tex_y = int(tex_pos) & 63
                tex_pos += step
                c = texture.get_at((tex_x, tex_y))

                # On NE side, darken the color of the texture. Looks nicer
                if side == 1:
                    c = darken_color(c, 2)

                screen.set_at((x, y), c)

        else:
            # Check which color we need to draw
            c = COLOR.white
            if tile == 'X':
                c = COLOR.gray
            if tile == '-':
                c = COLOR.white
            if tile == '1':
                c = COLOR.blue
            if tile == '2':
                c = COLOR.green
            if tile == '3':
                c = COLOR.red
            if tile == '4':
                c = COLOR.purple

            # On the NE facing side, we draw a darker color. Looks nicer
            if side == 1:
                c = darken_color(c, 2)

            # Draw the line (@TODO: texture)
            pg.draw.line(screen, c, (x, draw_start), (x, draw_end))


def generate_hud_map(player):
    map = pg.Surface( (MAPSIZE[0] * 10, MAPSIZE[1] * 10) )
    map.set_alpha(128)

    map.fill(COLOR.black)

    for y in range(0, MAPSIZE[0]):
        for x in range(0, MAPSIZE[1]):
            if get_tile_from_map(y, x) != ' ':
                map.fill(COLOR.white, ((x-1) * 10, (y-1) * 10, 10, 10))

    dot = pg.Surface((10, 10))
    pg.draw.circle(dot, COLOR.red, (5,5), 2)
    map.blit(dot, (int(player.x * 10), int(player.y * 10)))

    angle = math.atan2(player.dir_y, player.dir_x)
    map = pg.transform.rotate(map, math.degrees(angle))
    return map


def hud(screen, player):
    hud = []
    hud.append('X pos : %f' % (player.x))
    hud.append('Y pos : %f' % (player.y))
    hud.append('DX pos : %f' % (player.dir_x))
    hud.append('DY pos : %f' % (player.dir_y))
    hud.append('PX pos : %f' % (player.plane_x))
    hud.append('PY pos : %f' % (player.plane_y))

    font1 = pg.font.Font(pg.font.get_default_font(), 12)

    pos_y = 5
    for line in hud:
        text = font1.render(line, True, COLOR.white)
        # screen.fill((32, 32, 0), (5, pos_y - 5, 200, pos_y + 10))
        screen.blit(text, dest=(10, pos_y))
        pos_y += 15

    if DISPLAY_HUD_MAP:
        map = generate_hud_map(player)
        # screen.blit(map, dest=(WSIZE - 60, 10))
        screen.blit(map, dest=(10, 10))


def texture_floor_and_ceiling(screen, player, floor_texture, ceiling_texture):
    texture_w = floor_texture.get_width()
    texture_h = floor_texture.get_height()

    for y in range(H2SIZE + 1, HSIZE):
        ray_dir_x0 = player.dir_x - player.plane_x
        ray_dir_y0 = player.dir_y - player.plane_y
        ray_dir_x1 = player.dir_x + player.plane_x
        ray_dir_y1 = player.dir_y + player.plane_y

        p = y - H2SIZE
        pos_z = 0.5 * HSIZE
        row_distance = pos_z / p

        floor_step_x = row_distance * (ray_dir_x1 - ray_dir_x0) / WSIZE
        floor_step_y = row_distance * (ray_dir_y1 - ray_dir_y0) / WSIZE

        floor_x = player.x + (row_distance * ray_dir_x0)
        floor_y = player.y + (row_distance * ray_dir_y0)

        cell_x = int(floor_x)
        cell_y = int(floor_y)

        t_x = int(texture_w * (floor_x - cell_x)) & (texture_w - 1)
        t_y = int(texture_h * (floor_y - cell_y)) & (texture_h - 1)

        for x in range(0, WSIZE):
            cell_x = int(floor_x)
            cell_y = int(floor_y)

            t_x = int(texture_w * (floor_x - cell_x)) & (texture_w - 1)
            t_y = int(texture_h * (floor_y - cell_y)) & (texture_h - 1)

            floor_x += floor_step_x
            floor_y += floor_step_y

            c = floor_texture.get_at((t_x, t_y))
            screen.set_at((x, y), c)

            c = ceiling_texture.get_at((t_x, t_y))
            screen.set_at((x, HSIZE - y - 1), c)


def load_image(filename):
    image = pg.image.load(filename)
    return pg.transform.smoothscale(image, (64, 64))


def main():
    if len(MAP) != (MAPSIZE[0] * MAPSIZE[1]):
        print("Map size doesn't match")
        exit(1)

    pg.init()
    pg.display.set_caption('Wolf 3d')

    wall_textures = {}
    wall_textures['-'] = load_image('wall_tile_1.jpg')
    wall_textures['X'] = load_image('wall_tile_2.jpg')
    wall_textures['1'] = load_image('wall_tile_3.jpg')
    wall_textures['2'] = load_image('wall_tile_4.jpg')
    wall_textures['3'] = load_image('wall_tile_5.jpg')
    wall_textures['4'] = load_image('wall_tile_6.jpg')

    floor_texture = load_image('floor_tile_1.jpg')
    ceiling_texture = load_image('ceiling_tile_1.jpg')

    screen = pg.display.set_mode(WINSIZE)

    player = Player(12, 12, -1, 0)
    clock = pg.time.Clock()

    def tick():
        screen.fill(COLOR.black)
        # Paint ceiling and floor
        if TEXTURE_FLOORS_ENABLED:
            texture_floor_and_ceiling(screen, player, floor_texture, ceiling_texture)
        else:
            screen.fill(COLOR.ceil, (0, 0, WINSIZE[0], H2SIZE))
            screen.fill(COLOR.floor, (0, H2SIZE, WINSIZE[0], WINSIZE[1]))

        # Raycast walls
        ray_cast(screen, player, wall_textures)
        # Add sprites
        # Hud and stuff
        hud(screen, player)

    running = True
    while running:
        tick()

        speed = 0.1
        rot_speed = 0.1

        key = pg.key.get_pressed()
        if key[pg.K_UP]:
            if get_tile_from_map(int(player.x + player.dir_x * speed), int(player.y)) == ' ':
                player.x += player.dir_x * speed
            if get_tile_from_map(int(player.x), int(player.y + player.dir_y * speed)) == ' ':
                player.y += player.dir_y * speed

        if key[pg.K_DOWN]:
            if get_tile_from_map(int(player.x - player.dir_x * speed), int(player.y)) == ' ':
                player.x -= player.dir_x * speed
            if get_tile_from_map(int(player.x), int(player.y - player.dir_y * speed)) == ' ':
                player.y -= player.dir_y * speed

        if key[pg.K_LEFT]:
            old_dir_x = player.dir_x
            old_dir_y = player.dir_y
            player.dir_x = old_dir_x * math.cos(rot_speed) - old_dir_y * math.sin(rot_speed)
            player.dir_y = old_dir_x * math.sin(rot_speed) + old_dir_y * math.cos(rot_speed)

            old_plane_x = player.plane_x
            old_plane_y = player.plane_y
            player.plane_x = old_plane_x * math.cos(rot_speed) - old_plane_y * math.sin(rot_speed)
            player.plane_y = old_plane_x * math.sin(rot_speed) + old_plane_y * math.cos(rot_speed)

        if key[pg.K_RIGHT]:
            old_dir_x = player.dir_x
            old_dir_y = player.dir_y
            player.dir_x = old_dir_x * math.cos(-rot_speed) - old_dir_y * math.sin(-rot_speed)
            player.dir_y = old_dir_x * math.sin(-rot_speed) + old_dir_y * math.cos(-rot_speed)

            old_plane_x = player.plane_x
            old_plane_y = player.plane_y
            player.plane_x = old_plane_x * math.cos(-rot_speed) - old_plane_y * math.sin(-rot_speed)
            player.plane_y = old_plane_x * math.sin(-rot_speed) + old_plane_y * math.cos(-rot_speed)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # clock.tick()
        pg.display.flip()


if __name__ == "__main__":
    main()
