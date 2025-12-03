import os
import time
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from core.scheduler import greedy_coloring, dsatur_coloring, simulated_annealing_coloring
from core.graph_builder import build_conflict_graph_from_enrollments

def generate_density_plots():
    print("Generating Density vs Runtime Plots...")
    
    datasets = {
        "Small": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_014318",
        "Medium": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_014134",
        "Large": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_012151"
    }

    plt.style.use('ggplot')

    for size_name, path in datasets.items():
        print(f"\nProcessing {size_name} Dataset from: {path}")
        try:
            full_enrollments = pd.read_csv(os.path.join(path, "enrollments.csv"))
            full_courses = pd.read_csv(os.path.join(path, "courses.csv"))
            
            total_courses = len(full_courses)
            
            # Generate subsamples to get varying densities
            # We'll take 10 steps from 10% to 100%
            steps = [int(total_courses * p) for p in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
            steps = sorted(list(set([s for s in steps if s > 0])))
            
            densities = []
            greedy_times = []
            dsatur_times = []
            sa_times = []
            
            print(f"  Running subsampling on {steps} courses...")
            
            for n in steps:
                # Subset courses
                sub_courses = full_courses.head(n)
                sub_course_ids = set(sub_courses['course_id'])
                # Subset enrollments
                sub_enrollments = full_enrollments[full_enrollments['course_id'].isin(sub_course_ids)]
                
                G = build_conflict_graph_from_enrollments(sub_enrollments, sub_courses)
                
                # Calculate Density
                density = nx.density(G)
                densities.append(density)
                
                # Run Greedy
                start = time.time()
                res_greedy = greedy_coloring(G)
                greedy_times.append(time.time() - start)
                
                # Run DSATUR
                start = time.time()
                dsatur_coloring(G)
                dsatur_times.append(time.time() - start)
            
            # Plotting
            plt.figure(figsize=(10, 6))
            plt.scatter(densities, greedy_times, label="Greedy", color='blue', marker='o', s=80, alpha=0.7)
            plt.scatter(densities, dsatur_times, label="DSATUR", color='red', marker='s', s=80, alpha=0.7)
            
            plt.xlabel("Graph Density", fontsize=12)
            plt.ylabel("Runtime (seconds)", fontsize=12)
            plt.title(f"Graph Density vs Runtime ({size_name} Dataset)", fontsize=14)
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            
            filename = f"figure_density_runtime_{size_name.lower()}.png"
            plt.savefig(filename, dpi=300)
            print(f"  Saved {filename}")
            plt.close()

        except Exception as e:
            print(f"Error processing {size_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    generate_density_plots()
