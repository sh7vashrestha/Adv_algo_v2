import time
import os
import pandas as pd
import matplotlib.pyplot as plt
from core.scheduler import greedy_coloring, dsatur_coloring, simulated_annealing_coloring
from core.graph_builder import build_conflict_graph_from_enrollments



def run_custom_benchmark():
    print("\n==========================================")
    print("   Running Custom Dataset Benchmark")
    print("==========================================\n")

    # Define dataset paths provided by user
    datasets = {
        "Small": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_014318",
        # "Medium": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_014134",
        # "Large": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_012151"
    }

    results = {
        "Small": {},
        "Medium": {},
        "Large": {}
    }
    
    # Data for plotting
    plot_data = {
        "Courses": [],
        "Greedy_Time": [], "DSATUR_Time": [], "SA_Time": [],
        "Greedy_Color": [], "DSATUR_Color": [], "SA_Color": []
    }

    # Data for combined plotting (NOT USED anymore, but keeping structure if needed)
    # We will now generate plots PER dataset inside the loop
    
    # Order for iteration
    ordered_sizes = ["Small"] #, "Medium", "Large"]

    for size_name in ordered_sizes:
        path = datasets[size_name]
        print(f"\nProcessing {size_name} Dataset from: {path}")
        try:
            full_enrollments = pd.read_csv(os.path.join(path, "enrollments.csv"))
            full_courses = pd.read_csv(os.path.join(path, "courses.csv"))
            
            total_courses = len(full_courses)
            
            # --- Subsampling for Runtime Trend ---
            # Generate 5 data points: 20%, 40%, 60%, 80%, 100%
            steps = [int(total_courses * p) for p in [0.2, 0.4, 0.6, 0.8, 1.0]]
            # Ensure unique and non-zero
            steps = sorted(list(set([s for s in steps if s > 0])))
            
            subset_results = {
                "Courses": [],
                "Greedy": [], "DSATUR": [], "SA": []
            }
            
            print(f"  Running subsampling benchmark on {steps} courses...")
            
            final_colors = {} # Store colors for the full dataset (last step)
            
            for n in steps:
                # Subset courses
                sub_courses = full_courses.head(n)
                sub_course_ids = set(sub_courses['course_id'])
                # Subset enrollments
                sub_enrollments = full_enrollments[full_enrollments['course_id'].isin(sub_course_ids)]
                
                G = build_conflict_graph_from_enrollments(sub_enrollments, sub_courses)
                
                subset_results["Courses"].append(n)
                
                # 1. Greedy
                start = time.time()
                res_greedy = greedy_coloring(G)
                subset_results["Greedy"].append(time.time() - start)
                
                # 2. DSATUR
                start = time.time()
                res_dsatur = dsatur_coloring(G)
                subset_results["DSATUR"].append(time.time() - start)
                
                # 3. SA
                start = time.time()
                # Use Naive Initialization to force SA to run and show true trend
                # This prevents early exit when Greedy finds a perfect solution instantly
                k = res_greedy.num_periods 
                nodes = list(G.nodes())
                initial_coloring = {node: (i % k) + 1 for i, node in enumerate(nodes)}

                # Updated parameters as per user request: alpha=0.70, max_iters=3500
                # T0 updated to 1.0 to match frontend default
                res_sa = simulated_annealing_coloring(G, max_iters=3500, T0=1.0, alpha=0.70, initial=initial_coloring)
                subset_results["SA"].append(time.time() - start)
                
                # Update final_colors at every step; the last step (full dataset) will be the one used.
                final_colors["Greedy"] = res_greedy.num_periods
                final_colors["DSATUR"] = res_dsatur.num_periods
                final_colors["SA"] = res_sa.num_periods

            # --- Plot 1: Runtime vs Number of Courses (Trend for this dataset) ---
            plt.figure(figsize=(10, 6))
            plt.plot(subset_results["Courses"], subset_results["Greedy"], label="Greedy", marker='o', linewidth=2)
            plt.plot(subset_results["Courses"], subset_results["DSATUR"], label="DSATUR", marker='s', linewidth=2)
            plt.plot(subset_results["Courses"], subset_results["SA"], label="Simulated Annealing", marker='^', linewidth=2)
            plt.xlabel("Number of Courses (n)", fontsize=12)
            plt.ylabel("Runtime (seconds)", fontsize=12)
            plt.title(f"Runtime vs Number of Courses ({size_name} Dataset)", fontsize=14)
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            filename_trend = f"figure_runtime_trend_{size_name.lower()}.png"
            plt.savefig(filename_trend, dpi=300)
            print(f"Saved {filename_trend}")

            # --- Plot 2: Colors Used (Bar Chart for Full Dataset) ---
            labels = ['Greedy', 'DSATUR', 'Simulated Annealing']
            colors_used = [final_colors["Greedy"], final_colors["DSATUR"], final_colors["SA"]]
            
            plt.figure(figsize=(8, 6))
            bars = plt.bar(labels, colors_used, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            plt.ylabel("Number of Colors (Timeslots)", fontsize=12)
            plt.title(f"Colors Used by Each Algorithm ({size_name} Dataset)", fontsize=14)
            plt.grid(True, axis='y', linestyle='--', alpha=0.7)
            
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                         f'{int(height)}',
                         ha='center', va='bottom')
                         
            filename_color = f"figure_colors_{size_name.lower()}.png"
            plt.savefig(filename_color, dpi=300)
            print("Saved benchmark_sa_convergence.png")
            
        except Exception as e:
            print(f"Error processing {size_name}: {e}")
            import traceback
            traceback.print_exc()

def run_custom_benchmark():
    print("\n==========================================")
    print("   Running Custom Dataset Benchmark")
    print("==========================================\n")

    # Define dataset paths provided by user
    datasets = {
        "Small": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_155837",
        "Medium": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_014134",
        "Large": "/Users/kchowdh1/Desktop/KSU_Academic/Project/Adv_algo_v2/data/synthetic/20251202_012151"
    }

    final_stats = {
        "Small": {},
        "Medium": {},
        "Large": {}
    }
    
    # Data for plotting
    plot_data = {
        "Courses": [],
        "Greedy_Time": [], "DSATUR_Time": [], "SA_Time": [],
        "Greedy_Color": [], "DSATUR_Color": [], "SA_Color": []
    }

    # Data for combined plotting (NOT USED anymore, but keeping structure if needed)
    # We will now generate plots PER dataset inside the loop
    
    # Order for iteration
    ordered_sizes = ["Small", "Medium", "Large"]

    for size_name in ordered_sizes:
        path = datasets[size_name]
        print(f"\nProcessing {size_name} Dataset from: {path}")
        try:
            full_enrollments = pd.read_csv(os.path.join(path, "enrollments.csv"))
            full_courses = pd.read_csv(os.path.join(path, "courses.csv"))
            
            total_courses = len(full_courses)
            
            # --- Subsampling for Runtime Trend ---
            # Generate 5 data points: 20%, 40%, 60%, 80%, 100%
            steps = [int(total_courses * p) for p in [0.2, 0.4, 0.6, 0.8, 1.0]]
            # Ensure unique and non-zero
            steps = sorted(list(set([s for s in steps if s > 0])))
            
            subset_results = {
                "Courses": [],
                "Greedy": [], "DSATUR": [], "SA": []
            }
            
            print(f"  Running subsampling benchmark on {steps} courses...")
            
            final_colors = {} # Store colors for the full dataset (last step)
            
            for n in steps:
                # Subset courses
                sub_courses = full_courses.head(n)
                sub_course_ids = set(sub_courses['course_id'])
                # Subset enrollments
                sub_enrollments = full_enrollments[full_enrollments['course_id'].isin(sub_course_ids)]
                
                G = build_conflict_graph_from_enrollments(sub_enrollments, sub_courses)
                
                subset_results["Courses"].append(n)
                
                # 1. Greedy
                start = time.time()
                res_greedy = greedy_coloring(G)
                subset_results["Greedy"].append(time.time() - start)
                
                # 2. DSATUR
                start = time.time()
                res_dsatur = dsatur_coloring(G)
                subset_results["DSATUR"].append(time.time() - start)
                
                # 3. SA
                # Use Naive Initialization to force SA to run and show true trend
                # This prevents early exit when Greedy finds a perfect solution instantly
                k = res_greedy.num_periods 
                nodes = list(G.nodes())
                initial_coloring = {node: (i % k) + 1 for i, node in enumerate(nodes)}

                start = time.time()
                # Updated parameters as per user request: alpha=0.70, max_iters=3500
                # T0 updated to 1.0 to match frontend default
                res_sa = simulated_annealing_coloring(G, max_iters=3500, T0=1.0, alpha=0.70, initial=initial_coloring)
                subset_results["SA"].append(time.time() - start)
                
                # Update final_colors at every step; the last step (full dataset) will be the one used.
                final_colors["Greedy"] = res_greedy.num_periods
                final_colors["DSATUR"] = res_dsatur.num_periods
                final_colors["SA"] = res_sa.num_periods

            # --- Plot 1: Runtime vs Number of Courses (Trend for this dataset) ---
            plt.figure(figsize=(10, 6))
            plt.plot(subset_results["Courses"], subset_results["Greedy"], label="Greedy", marker='o', linewidth=2)
            plt.plot(subset_results["Courses"], subset_results["DSATUR"], label="DSATUR", marker='s', linewidth=2)
            plt.plot(subset_results["Courses"], subset_results["SA"], label="Simulated Annealing", marker='^', linewidth=2)
            plt.xlabel("Number of Courses (n)", fontsize=12)
            plt.ylabel("Runtime (seconds)", fontsize=12)
            plt.title(f"Runtime vs Number of Courses ({size_name} Dataset)", fontsize=14)
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            filename_trend = f"figure_runtime_trend_{size_name.lower()}.png"
            plt.savefig(filename_trend, dpi=300)
            print(f"Saved {filename_trend}")

            # --- Plot 2: Colors Used (Bar Chart for Full Dataset) ---
            labels = ['Greedy', 'DSATUR', 'Simulated Annealing']
            colors_used = [final_colors["Greedy"], final_colors["DSATUR"], final_colors["SA"]]
            
            plt.figure(figsize=(8, 6))
            bars = plt.bar(labels, colors_used, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            plt.ylabel("Number of Colors (Timeslots)", fontsize=12)
            plt.title(f"Colors Used by Each Algorithm ({size_name} Dataset)", fontsize=14)
            plt.grid(True, axis='y', linestyle='--', alpha=0.7)
            
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                         f'{int(height)}',
                         ha='center', va='bottom')
                         
            filename_color = f"figure_colors_{size_name.lower()}.png"
            plt.savefig(filename_color, dpi=300)
            print(f"Saved {filename_color}")
            
            # Print Table Row Data (using full dataset results)
            # We can't print the full table easily in this loop structure without storing, 
            # but we can print the final stats for verification
            print(f"  Final Stats ({size_name}): Greedy={subset_results['Greedy'][-1]:.4f}s, DSATUR={subset_results['DSATUR'][-1]:.4f}s, SA={subset_results['SA'][-1]:.4f}s")



            final_stats[size_name] = {
                "Greedy": {"time": subset_results["Greedy"][-1], "colors": final_colors["Greedy"]},
                "DSATUR": {"time": subset_results["DSATUR"][-1], "colors": final_colors["DSATUR"]},
                "SA": {"time": subset_results["SA"][-1], "colors": final_colors["SA"]}
            }

        except Exception as e:
            print(f"Error processing {size_name}: {e}")
            import traceback
            traceback.print_exc()

    # --------------------------------------------------------------------------
    # PRINT SUMMARY TABLE
    # --------------------------------------------------------------------------
    print("\n" + "="*100)
    
    # Top Header
    print(f"| {'':<20} | {'Small Dataset':^23} | {'Medium Dataset':^23} | {'Large Dataset':^23} |")
    print(f"| {'Algorithm':<20} +-----------+-----------+-----------+-----------+-----------+-----------|")
    print(f"| {'':<20} | {'Runtime':^9} | {'Color':^9} | {'Runtime':^9} | {'Color':^9} | {'Runtime':^9} | {'Color':^9} |")
    print(f"| {'':<20} | {'':^9} | {'Used':^9} | {'':^9} | {'Used':^9} | {'':^9} | {'Used':^9} |")
    print("|" + "-"*22 + "+" + "-"*11 + "+" + "-"*11 + "+" + "-"*11 + "+" + "-"*11 + "+" + "-"*11 + "+" + "-"*11 + "|")
    
    for algo in ["Greedy", "DSATUR", "Simulated Annealing"]:
        algo_key = "SA" if algo == "Simulated Annealing" else algo
        
        # Handle long name wrapping for Simulated Annealing if needed, 
        # but 20 chars is enough for "Simulated Annealing" (19 chars).
        
        row_str = f"| {algo:<20} |"
        
        for size in ["Small", "Medium", "Large"]:
            stats = final_stats[size].get(algo_key)
            if stats:
                # Format: "0.0002 s " and "  40   "
                row_str += f" {stats['time']:.4f} s | {stats['colors']:^9} |"
            else:
                row_str += f" {'N/A':^9} | {'N/A':^9} |"
        
        print(row_str)
        print("|" + "-"*22 + "+" + "-"*11 + "+" + "-"*11 + "+" + "-"*11 + "+" + "-"*11 + "+" + "-"*11 + "+" + "-"*11 + "|")

    print("="*100 + "\n")

if __name__ == "__main__":
    run_custom_benchmark()
