import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

def plot_distribuicao_anual(df,column_to_plot,save_dir=''):
    
    data = df
    data['year'] = data.index.year
    
    plt.figure(figsize = (15, 8))
    pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
    g = sns.FacetGrid(data, row="year",hue="year",aspect=15, height=.5, palette=pal)
    

    # Draw the densities in a few steps
    g.map(sns.kdeplot, column_to_plot, clip_on=False, shade=True, alpha=1, lw=1.5, bw=.2)
    g.map(sns.kdeplot, column_to_plot, clip_on=False, color="w", lw=2, bw=.2)
    g.map(plt.axhline, y=0, lw=2, clip_on=False)


    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)


    g.map(label, column_to_plot)

    # Set the subplots to overlap
    g.fig.subplots_adjust(hspace=-.25)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[])
    g.despine(bottom=True, left=True)

    
    if(len(save_dir)>0):
        name = column_to_plot+' ao longo dos anos'
        plt.savefig(os.path.join(save_dir,name+'.png'), dpi = 200)

    plt.show()
