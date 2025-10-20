from .models.node import NodeModel
from .models.unload import UnloadModel

def find(path: str, nodes:dict[str, NodeModel]) -> list[NodeModel]:
    found:set[str] = set()
    result:list[NodeModel] = []
    for key in nodes.keys():
        if path in key:
            found.add(key)
            result.append(nodes[key])
    for node in nodes.values():
        if isinstance(node.data, UnloadModel):
            if path in node.data.source and node.full_path not in found:
                result.append(node)
                found.add(node.full_path)
            for destination in node.data.destinations:
                if path in destination.dst and node.full_path not in found:
                    result.append(node)
                    found.add(node.full_path)
    return result