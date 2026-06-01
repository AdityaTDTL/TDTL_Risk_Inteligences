from __future__ import annotations
import networkx as nx


def build_relationship_graph(records: list[dict]) -> nx.Graph:
    graph = nx.Graph()
    for row in records:
        customer = f"customer:{row.get('customer_id')}"
        source = f"account:{row.get('source_account')}"
        agent = f"agent:{row.get('agent_id')}"
        branch = f"branch:{row.get('branch')}"
        for node in [customer, source, agent, branch]:
            graph.add_node(node)
        graph.add_edge(customer, source, relation="paid_from")
        graph.add_edge(customer, agent, relation="handled_by")
        graph.add_edge(agent, branch, relation="belongs_to")
    return graph


def collusion_indicators(records: list[dict]) -> dict:
    graph = build_relationship_graph(records)
    degree = nx.degree_centrality(graph)
    suspicious_nodes = sorted(degree.items(), key=lambda item: item[1], reverse=True)[:10]
    account_clusters = []
    for node in graph.nodes:
        if node.startswith("account:"):
            customers = [n for n in graph.neighbors(node) if n.startswith("customer:")]
            if len(customers) >= 3:
                account_clusters.append({"source_account": node.replace("account:", ""), "linked_customers": len(customers), "customers": customers})
    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "top_connected_nodes": suspicious_nodes,
        "suspicious_shared_funding_accounts": account_clusters,
        "risk_category": "Critical" if account_clusters else "Low",
    }
