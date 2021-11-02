import numpy as np
import matplotlib.pyplot as plt

class Punto2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Area:
    def __init__(self, cx, cy, w, h):
        self.cx, self.cy = cx, cy
        self.w, self.h = w, h
        self.west_edge, self.east_edge = cx - w/2, cx + w/2
        self.north_edge, self.south_edge = cy - h/2, cy + h/2

    def contains(self, point):
        try:
            point_x, point_y = point.x, point.y
        except AttributeError:
            point_x, point_y = point

        return self.west_edge <= point_x < self.east_edge and self.north_edge <= point_y < self.south_edge

    def intersects(self, other):
        return not (other.west_edge > self.east_edge or
                    other.east_edge < self.west_edge or
                    other.north_edge > self.south_edge or
                    other.south_edge < self.north_edge)

    def draw(self, ax, c='k', lw=1, **kwargs):
        x1, y1 = self.west_edge, self.north_edge
        x2, y2 = self.east_edge, self.south_edge
        ax.plot([x1,x2,x2,x1,x1],[y1,y1,y2,y2,y1], c=c, lw=lw, **kwargs)


class QuadTree:
    def __init__(self, boundary, max_points=4, depth=0):
        self.boundary = boundary
        self.max_points = max_points
        self.points = []
        self.depth = depth
        self.divided = False

    def divide(self):
        cx, cy = self.boundary.cx, self.boundary.cy
        w, h = self.boundary.w / 2, self.boundary.h / 2

        self.nw = QuadTree(Area(cx - w/2, cy - h/2, w, h),
                           self.max_points, self.depth + 1)
        self.ne = QuadTree(Area(cx + w/2, cy - h/2, w, h),
                            self.max_points, self.depth + 1)
        self.se = QuadTree(Area(cx + w/2, cy + h/2, w, h),
                            self.max_points, self.depth + 1)
        self.sw = QuadTree(Area(cx - w/2, cy + h/2, w, h),
                            self.max_points, self.depth + 1)

        self.divided = True

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        if len(self.points) < self.max_points:
            self.points.append(point)
            return True

        if not self.divided:
            self.divide()

        return (self.ne.insert(point) or
                self.nw.insert(point) or
                self.se.insert(point) or
                self.sw.insert(point))


    def busqueda_Rango(self, boundary, found_points):
        if not self.boundary.intersects(boundary):
            return False

        for point in self.points:
            if boundary.contains(point):
                found_points.append(point)

        if self.divided:
            self.nw.busqueda_Rango(boundary, found_points)
            self.ne.busqueda_Rango(boundary, found_points)
            self.se.busqueda_Rango(boundary, found_points)
            self.sw.busqueda_Rango(boundary, found_points)
        return found_points

    #sobrecarga para devolver el numero de nodos del arbol
    def __len__(self):
        npoints = len(self.points)
        if self.divided:
            npoints += len(self.nw)+len(self.ne)+len(self.se)+len(self.sw)
        return npoints

    def draw(self, ax):

        self.boundary.draw(ax)

        if self.divided:
            self.nw.draw(ax)
            self.ne.draw(ax)
            self.se.draw(ax)
            self.sw.draw(ax)




DPI = 72  #Para el grosor de los contornos
np.random.seed(5) #Semilla para los numeros aleatorios

width, height = 500, 500  #Para el tamaño del grafico y los limites para generar los puntos

N = 500 #Numero de nodos

coords = np.random.randn(N, 2) * height/3 + ((width/2) , (height/2))
points = [Punto2D(*coord) for coord in coords]

#El dominio es el area en el que se generara el quad tree
domain = Area(width/2, height/2, width, height)
qtree = QuadTree(domain)
#Se insertan los puntos al arbol
for point in points:
    qtree.insert(point)

print(qtree.ne.sw.divided)
print(qtree.ne.sw.boundary.cx)
print(len(qtree.ne.sw.points))
print(qtree.ne.sw.depth)

print('Numero de puntos en el dominio =', len(qtree))

#Para generar el grafico del QuadTree
fig = plt.figure(figsize=(width/DPI, height/DPI), dpi=DPI)
ax = plt.subplot()
ax.set_xlim(0, width)
ax.set_ylim(0, height)
qtree.draw(ax)

ax.scatter([p.x for p in points], [p.y for p in points], s=4)
ax.set_xticks([])
ax.set_yticks([])

# Area(x,y,ancho,largo) x, y son puntos del centro del rectangulo
region = Area(140, 190, 150, 150)

#Para la busqueda dentro del area
found_points = []
qtree.busqueda_Rango(region, found_points)
print('Numero de puntos en el area  =', len(found_points))

#Para resaltar los puntos dentro del area
ax.scatter([p.x for p in found_points], [p.y for p in found_points],
           facecolors='none', edgecolors='r', s=32)
region.draw(ax, c='r')

#Para generar la imagen
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('quadtree.png')
plt.show()