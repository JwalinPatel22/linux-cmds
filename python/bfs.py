from manim import *
import random
import math

# Manim script: BFS vs Random Walk visualization
# Designed for Manim Community (manim>=0.16)
# Scene: Split screen showing the same maze on left (random walk) and right (BFS)

GRID_SIZE = 12
CELL_SIZE = 0.5
WALL_PROB = 0.28
SEED = 42

class BFSVsRandomWalkScene(Scene):
    def construct(self):
        random.seed(SEED)

        # Create the maze as a 2D boolean grid: True = free, False = wall
        maze = self._generate_maze(GRID_SIZE, WALL_PROB, seed=SEED)
        start = (0, 0)
        goal = (GRID_SIZE - 1, GRID_SIZE - 1)
        maze[start[1]][start[0]] = True
        maze[goal[1]][goal[0]] = True

        # Build left and right grid VGroups (they share the same maze layout)
        left_grid = self._build_grid(maze, label="Random Walk")
        right_grid = self._build_grid(maze, label="Breadth-First Search")

        # Position them side by side
        left_grid.shift(LEFT * (GRID_SIZE * CELL_SIZE / 1.5))
        right_grid.shift(RIGHT * (GRID_SIZE * CELL_SIZE / 1.5))

        # Add both grids
        self.add(left_grid, right_grid)

        # Add start and goal markers
        left_start_dot = self._place_marker(left_grid, start, color=GREEN)
        left_goal_dot = self._place_marker(left_grid, goal, color=RED)
        right_start_dot = self._place_marker(right_grid, start, color=GREEN)
        right_goal_dot = self._place_marker(right_grid, goal, color=RED)

        # Time counters
        rw_counter = Integer(0).scale(0.7)
        bfs_counter = Integer(0).scale(0.7)
        rw_label = VGroup(Text("Time"), rw_counter).arrange(RIGHT, buff=0.15)
        bfs_label = VGroup(Text("Time"), bfs_counter).arrange(RIGHT, buff=0.15)
        rw_label.to_edge(UL).shift(RIGHT * 0.5)
        bfs_label.to_edge(UR).shift(LEFT * 0.5)
        self.add(rw_label, bfs_label)

        # Create random walker on left
        left_center_points = self._grid_centers(left_grid)
        rw_dot = Dot(left_center_points[start]).set_color(BLUE).scale(0.5)
        rw_trail = VMobject().set_stroke(width=2, opacity=0.7).set_color(rgb_to_color([0.6,0.85,1]))
        rw_trail.set_points_as_corners([left_center_points[start], left_center_points[start]])
        self.add(rw_dot, rw_trail)

        # BFS preprocessing (compute layers and parent pointers)
        bfs_layers, parent = self._bfs_layers(maze, start, goal)

        # Prepare visual layers for right grid (for fast lookup)
        right_squares = self._square_dict(right_grid)
        left_squares = self._square_dict(left_grid)

        # Create queue visual (bottom-right corner)
        queue_box = self._build_queue_box().scale(0.9).to_corner(DR)
        queue_box.shift(LEFT * 0.4 + UP * 0.4)
        self.add(queue_box)

        # Anim trackers and flags
        random_running = ValueTracker(1)  # 1 = running, 0 = stopped
        rw_steps = ValueTracker(0)
        bfs_steps = ValueTracker(0)

        # Random walker updater: moves randomly step-by-step
        rw_state = {
            "pos": start,
            "last_move_time": 0.0,
            "step_interval": 0.25,
        }

        def rw_updater(mobj, dt):
            if random_running.get_value() < 0.5:
                return
            rw_state["last_move_time"] += dt
            if rw_state["last_move_time"] < rw_state["step_interval"]:
                return
            rw_state["last_move_time"] = 0
            x, y = rw_state["pos"]
            neighbors = self._neighbors((x, y), maze)
            if not neighbors:
                return
            nx, ny = random.choice(neighbors)
            rw_state["pos"] = (nx, ny)
            target = left_center_points[(nx, ny)]
            # move dot and append to trail
            mobj.move_to(target)
            # append a small segment
            pts = list(rw_trail.get_points())
            pts.extend([target])
            rw_trail.set_points_as_corners(pts)
            rw_steps.increment_value(1)
            rw_counter.set_value(int(rw_steps.get_value()))

        rw_dot.add_updater(rw_updater)

        # Small entrance animation
        self.play(AnimationGroup(FadeIn(left_grid, shift=LEFT * 0.3), FadeIn(right_grid, shift=RIGHT * 0.3), lag_ratio=0.1))
        self.wait(0.4)

        # START two processes: random walker is running via updater, BFS we animate layer-by-layer
        # We animate BFS layers sequentially while random walker uppdater runs concurrently

        # Play BFS wavefront
        for layer_index, layer in enumerate(bfs_layers):
            # Visual effect: highlight all nodes in this layer
            anims = []
            for node in layer:
                sq = right_squares[node]
                target_color = interpolate_color(YELLOW, ORANGE, layer_index / (len(bfs_layers) or 1))
                anims.append(sq.animate.set_fill(target_color, opacity=0.9))
            # Enqueue visual: show items being enqueued
            self.play(AnimationGroup(*anims, run_time=0.45))
            # update BFS counter and the queue box
            bfs_steps.increment_value(1)
            bfs_counter.set_value(int(bfs_steps.get_value()))
            # animate queue push/pop for this layer
            self._animate_queue_push(queue_box, len(layer), self)

            # Check if goal reached in this layer
            if goal in layer:
                # flash the goal
                goal_sq = right_squares[goal]
                self.play(Flash(goal_sq, color=GREEN, flash_radius=0.9))
                # stop the random walker (freeze left side)
                random_running.set_value(0)
                # pause slightly to show the moment
                self.wait(0.4)
                break

        # Backtrack shortest path using parent dict
        path = self._reconstruct_path(parent, start, goal)
        # Highlight path with bold purple
        path_anims = []
        for p in path:
            sq = right_squares[p]
            path_anims.append(sq.animate.set_fill(PURPLE, opacity=1.0))
            path_anims.append(sq.animate.set_stroke(width=3))
        self.play(AnimationGroup(*path_anims, lag_ratio=0.08, run_time=1.2))

        # Zoom into BFS path while freezing left
        self.play(self.camera.frame.animate.scale(0.85).move_to(right_grid.get_center()))
        # overlay texts
        left_text = Text("Random Walk: No guarantee, inefficient.").scale(0.6).set_color(GREY_A)
        right_text = Text("Breadth-First Search: Guaranteed shortest path.").scale(0.65).set_color(WHITE)
        left_text.next_to(left_grid, DOWN)
        right_text.next_to(right_grid, DOWN)
        self.add(left_text, right_text)
        self.wait(0.8)

        # Freeze left side visual: make it look messy by giving motion blur (simulate by reducing opacity)
        self.play(left_grid.animate.set_opacity(0.25), run_time=0.8)

        # Fade out random walk side
        self.play(FadeOut(left_grid), FadeOut(left_text), FadeOut(left_start_dot), FadeOut(left_goal_dot), FadeOut(rw_dot), FadeOut(rw_trail))
        self.wait(0.3)

        # Keep BFS path glowing from start->purple->goal with a subtle shimmer
        shimmer = Succession(*[Indicate(right_squares[p], scale_factor=1.05) for p in path], run_time=2.2)
        self.play(shimmer)

        # Narration cue text
        narration = Text("BFS always guarantees the shortest path — because it explores in perfect layers, leaving nothing unchecked.").scale(0.6)
        narration.to_edge(DOWN)
        self.play(FadeIn(narration))
        self.wait(2.0)

    # ---------- Helper methods ----------
    def _generate_maze(self, n, wall_prob=0.3, seed=None):
        if seed is not None:
            random.seed(seed)
        maze = [[random.random() > wall_prob for _ in range(n)] for _ in range(n)]
        return maze

    def _build_grid(self, maze, label=""):
        n = len(maze)
        squares = VGroup()
        for j in range(n):
            for i in range(n):
                sq = Square(side_length=CELL_SIZE, stroke_width=0.5)
                sq.move_to(np.array([(i - (n - 1)/2) * CELL_SIZE, ( (n - 1)/2 - j) * CELL_SIZE, 0]))
                if not maze[j][i]:
                    sq.set_fill(GREY_B, opacity=1.0).set_stroke(width=0.5, color=GREY_C)
                else:
                    sq.set_fill(WHITE, opacity=0.9).set_stroke(width=0.5, color=GREY_C)
                # subtle drop shadow: duplicate with low opacity and slightly offset
                shadow = sq.copy().set_fill(BLACK, opacity=0.06).set_stroke(width=0)
                shadow.shift(DOWN * 0.025 + RIGHT * 0.025)
                group = VGroup(shadow, sq)
                group.square = sq
                squares.add(group)
        # Add label
        title = Text(label).scale(0.6)
        title.next_to(squares, UP)
        container = VGroup(squares, title)
        return container

    def _square_dict(self, grid_vgroup):
        # grid_vgroup[0] is squares VGroup consisting of groups of (shadow, sq)
        squares_vg = grid_vgroup[0]
        n = int(math.sqrt(len(squares_vg)))
        # Build mapping from (i,j) to the actual Square (the visible one, not the shadow)
        d = {}
        index = 0
        for j in range(n):
            for i in range(n):
                grp = squares_vg[index]
                d[(i, j)] = grp.square
                index += 1
        return d

    def _grid_centers(self, grid_vgroup):
        squares_vg = grid_vgroup[0]
        n = int(math.sqrt(len(squares_vg)))
        centers = {}
        index = 0
        for j in range(n):
            for i in range(n):
                grp = squares_vg[index]
                # square is grp.square
                centers[(i, j)] = grp.square.get_center()
                index += 1
        return centers

    def _place_marker(self, grid_vgroup, coord, color=GREEN):
        centers = self._grid_centers(grid_vgroup)
        c = centers[coord]
        square = Dot(c).set_color(color).scale(0.9)
        self.add(square)
        return square

    def _neighbors(self, node, maze):
        x, y = node
        n = len(maze)
        neigh = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n and maze[ny][nx]:
                neigh.append((nx, ny))
        return neigh

    def _bfs_layers(self, maze, start, goal):
        from collections import deque
        n = len(maze)
        q = deque()
        q.append(start)
        visited = {start}
        parent = {start: None}
        layers = []
        while q:
            layer_size = len(q)
            layer = []
            for _ in range(layer_size):
                node = q.popleft()
                layer.append(node)
                if node == goal:
                    layers.append(layer)
                    return layers, parent
                for nb in self._neighbors(node, maze):
                    if nb not in visited:
                        visited.add(nb)
                        parent[nb] = node
                        q.append(nb)
            layers.append(layer)
        return layers, parent

    def _reconstruct_path(self, parent, start, goal):
        if goal not in parent:
            return []
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur, None)
        path.reverse()
        return path

    def _build_queue_box(self):
        box = RoundedRectangle(corner_radius=0.12, height=1.2, width=2.4)
        title = Text("Queue", font_size=20).move_to(box.get_top() + DOWN * 0.18)
        contents = VGroup()  # container for small squares
        contents.next_to(title, DOWN, buff=0.12)
        container = VGroup(box, title, contents)
        return container

    def _animate_queue_push(self, queue_box, count, scene):
        # This is a light-weight visual: create small squares that pop into the queue then fade
        box = queue_box[0]
        contents = queue_box[2]
        anims = []
        for i in range(min(6, count)):
            sq = Square(side_length=0.18).set_fill(GREY_A, opacity=0.9).set_stroke(width=0.5)
            target_x = box.get_left()[0] + 0.18 * (i + 1)
            target_y = box.get_top()[1] - 0.35
            sq.move_to(np.array([target_x, target_y, 0]))
            anims.append(FadeIn(sq, shift=DOWN * 0.05))
            anims.append(FadeOut(sq, shift=UP * 0.05))
        scene.play(AnimationGroup(*anims, lag_ratio=0.12, run_time=0.6))

# Notes for running:
# manim -pql bfs_vs_random_walk_manim.py BFSVsRandomWalkScene
# Adjust resolution and quality flags as needed (-pqh for higher quality)

