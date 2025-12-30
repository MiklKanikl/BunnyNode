import heapq

def shortest_path(graph, start, end):
    pq = [(0, start)]
    dist = {start: 0}
    prev = {}

    while pq:
        d, n = heapq.heappop(pq)
        if n == end:
            break
        for neigh, w in graph[n]:
            nd = d + w
            if neigh not in dist or nd < dist[neigh]:
                dist[neigh] = nd
                prev[neigh] = n
                heapq.heappush(pq, (nd, neigh))

    return dist.get(end), prev

def build_path(prev, start, end):
    p = []
    n = end
    while n != start:
        p.append(n)
        n = prev.get(n)
        if n is None:
            return []
    p.append(start)
    return list(reversed(p))