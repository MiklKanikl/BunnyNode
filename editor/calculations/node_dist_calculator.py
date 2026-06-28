import math

class ShapeBorderCalculator:
    @staticmethod
    def rect(width, height, angle_rad):
        half_w = width / 2
        half_h = height / 2
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        if abs(cos_a) < 1e-10:
            cos_a = 1e-10
        if abs(sin_a) < 1e-10:
            sin_a = 1e-10
        
        t_x = half_w / abs(cos_a)
        t_y = half_h / abs(sin_a)
        return min(t_x, t_y)
    
    @staticmethod
    def ellipse(width, height, angle_rad):
        a = width / 2
        b = height / 2
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        if abs(cos_a) < 1e-10 and abs(sin_a) < 1e-10:
            return 0
        
        return (a * b) / math.sqrt((b * cos_a) ** 2 + (a * sin_a) ** 2)
    
    @staticmethod
    def triangle(width, height, angle_rad):
        half_w = width / 2
        half_h = height / 2
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        points = [
            (0, -half_h),
            (-half_w, half_h),
            (half_w, half_h)
        ]
        
        return ShapeBorderCalculator._intersect_polygon(points, cos_a, sin_a)
    
    @staticmethod
    def _intersect_polygon(points, cos_a, sin_a):
        n = len(points)
        distances = []
        
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            
            dx = x2 - x1
            dy = y2 - y1
            
            denom = dx * sin_a - dy * cos_a
            if abs(denom) < 1e-10:
                continue
            
            t = (x1 * sin_a - y1 * cos_a) / denom
            if t < 0 or t > 1:
                continue
            
            dist = t * math.sqrt(dx * dx + dy * dy)
            distances.append(dist)
        
        if not distances:
            return 0
        
        return min(distances)