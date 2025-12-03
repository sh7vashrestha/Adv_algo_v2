import os
import pandas as pd
import matplotlib.pyplot as plt
import random
from core.scheduler import simulated_annealing_coloring, greedy_coloring
from core.graph_builder import build_conflict_graph_from_enrollments

def generate_convergence_plots():
    print("Generating SA Convergence Plots...")
    
    datasets = {
        "Small": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_014318",
        "Medium": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_014134",
        "Large": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_012151"
    }

    plt.style.use('ggplot')
    
    # Store histories to plot together
    histories = {}

    for size_name, path in datasets.items():
        print(f"\nProcessing {size_name} Dataset from: {path}")
        try:
            enrollments = pd.read_csv(os.path.join(path, "enrollments.csv"))
            courses = pd.read_csv(os.path.join(path, "courses.csv"))
            
            print(f"  Building Graph...")
            G = build_conflict_graph_from_enrollments(enrollments, courses)
            
            # 1. Run Greedy first to determine a target number of colors (k)
            # This ensures we are using a realistic number of colors
            greedy_res = greedy_coloring(G)
            k = greedy_res.num_periods
            print(f"  Greedy found {k} colors. Initializing SA with Naive Modulo {k}-coloring...")
            
            # 2. Create a Naive Deterministic initial coloring
            # Assign colors based on node index modulo k. This is deterministic (not random)
            # but creates conflicts that SA needs to resolve, showing the convergence behavior.
            nodes = list(G.nodes())
            # Map node IDs to integers if they aren't already, or just enumerate
            initial_coloring = {node: (i % k) + 1 for i, node in enumerate(nodes)}
            
            print(f"  Running Simulated Annealing (alpha=0.70, max_iters=3500)...")
            # Run SA with specified parameters and Naive initialization
            res = simulated_annealing_coloring(G, max_iters=3500, T0=2.0, alpha=0.70, initial=initial_coloring)
            
            if res.history:
                histories[size_name] = res.history
            else:
                print("  Warning: No history returned from SA.")

        except Exception as e:
            print(f"Error processing {size_name}: {e}")
            import traceback
            traceback.print_exc()

    # Plot Combined Figure
    if histories:
        plt.figure(figsize=(10, 6))
        
        colors = {"Small": "blue", "Medium": "orange", "Large": "green"}
        
        for size_name, history in histories.items():
            plt.plot(history, label=f"{size_name} Dataset", color=colors.get(size_name, "black"), linewidth=1.5, alpha=0.8)
            
        plt.xlabel("Iterations", fontsize=12)
        plt.ylabel("Number of Conflicts", fontsize=12)
        plt.title("SA Convergence Curve (Combined)", fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        filename = "figure_sa_convergence_combined.png"
        plt.savefig(filename, dpi=300)
        print(f"\nSaved combined plot to {filename}")
    else:
        print("No data to plot.")

if __name__ == "__main__":
    generate_convergence_plots()
