# Downstream analyses

This document outlines some potential next steps after deriving embeddings from the audio data. Embedding-based workflows like this are now fairly standard in large-scale bioacoustics and soundscape ecology, and unlock a lot of analyses that would be painful or impossible on raw audio.

## Overview

After deriving embeddings, the ~100 GB compressed representations of the multi-TB dataset enable a wide range of downstream analyses that would be computationally prohibitive on raw audio. Some typical use cases (summarizing for inspiration) include:

- Training custom classifiers
- Active learning and smarter annotation
- Unsupervised exploration and pattern discovery
- Supervised work on vocal signatures and behavior
- Temporal, ecological and song-learning questions

This is all off the top of my (@nilomr) head, not an exhaustive list or a technical document. Just some ideas to get you started.

## Train custom classifiers

**Shallow classification heads**  
Train lightweight NNs on the embeddings to identify site-specific patterns, predict phenology, call types, whatever. Perch's 1536-dimensional embeddings already encode rich bioacoustic features, so simple models very often achieve strong performance with minimal labeled data. This will be especially useful for species for which performance of the original model is not optimal due to geographic variation, under-representation in training data, Wytham idiosyncrasies in terms of audio quality, background noise, etc.

**Few-shot learning**  
With very few labeled examples per class, linear probes on these embeddings can achieve very good results, if you want to squeeze extra performance out of the data without investing in large-scale annotation efforts and training a Wytham specialist model from scratch.

## Active learning and efficient annotation

This is a big one for large datasets like this, and likely necessary if you want to analyse species other than the very common ones in the Wytham dataset . The latter will have so many detections that activity patterns can be already inferred with great accuracy without strong classifiers. How to go about this:  
- Begin with the pretrained Perch predictions as a starting point. These will be pretty good for common species, less so for rare ones.
- Use uncertainty sampling or embedding-space diversity sampling to identify the most informative clips for manual annotation.

See an example of a similarr approach here: [Google Research's Perch notebook](https://github.com/google-research/perch/blob/main/agile_modeling.ipynb) (the folks at Google call it "agile modeling", annoyingly).

> ## IMPORTANT NOTE ON CALIBRATION
>
> When using embeddings for classification or active learning, be aware that the Perch model's output probabilities are raw neural network logits, not calibrated probabilities. This means that the confidence scores may not accurately reflect true likelihoods of correctness. For example, a prediction with a score of 0.9 does not mean there is a 90% chance that the prediction is correct. Any work that relies on these confidence scores (e.g., uncertainty sampling in active learning) should take this into account. You will need to apply calibration techniques (e.g., Platt scaling, isotonic regression) on a validation set to improve the reliability of these scores before using them in downstream tasks. See some relevant literature on model calibration:
>
> - Schwinger, R., McEwen, B., Kather, V. S., Heinrich, R., Rauch, L., & Tomforde, S. (2025). Uncertainty Calibration of Multi-Label Bird Sound Classifiers. arXiv preprint arXiv:2511.08261. https://arxiv.org/abs/2511.08261
> - Wood, C. M., & Kahl, S. (2024). Guidelines for appropriate use of BirdNET scores and other detector outputs. Journal of Ornithology. https://doi.org/10.1007/s10336-024-02144-5



## More-or-less unsupervised pattern discovery

(a favourite of mine)

**Clustering and visualization**  
Apply your favourite nonlinear dimensionality reduction algo to project embeddings into 2D/3D space for exploratory analysis. Used with care, clustering algos like HDBSCAN or hierarchical clustering on lower-dimensional spaces (but not as low as what you'd use for visualization!) can reveal acoustic communities, identify rare call types, detect recording artifacts, spot interesting sound events, etc.

See the [Wytham Viewer demo](https://abewythamviewer.vercel.app/) ([source](https://github.com/nilomr/ABE2025-WythamViewer)) if you want an interactive way to explore embeddings – this is more of an educational demo than a production tool but might spark some ideas.

**Nearest-neighbour retrieval**  
A very handy thing to do is to build a nearest-neighbour search index on embeddings so you can query “find things that sound like this clip” and rapidly retrieve similar events across the entire dataset. This is especially useful for rare or weird sound classes discovered during exploratory analyses, or in the context of new class discovery. I used this approach extensively to build a method to re-identify individual birds in this paper: [Merino Recalde et al., 2024 Curr. Biol.](https://www.cell.com/current-biology/fulltext/S0960-9822(25)00150-2).

You can also use this retrieval setup for rapid error analysis of classifiers: pull up false positives/negatives in embedding space and see what they cluster with, which often reveals systematic confusions or label issues.

## Supervised pattern discovery

Once you isolate and validate detections for a species, embeddings enable several types of fine-grained analyses:

### Individual vocal signatures

For species with individually distinctive vocalizations, embeddings could be used to discern individual signatures and track individual vocal activity across space and time. This is tricky if individuals have song repertoires. but feasible for species with stereotyped calls or songs.

### Behavioral context classification

Embeddings can potentially classify different vocalization types within a species (e.g., alarm calls vs. contact calls vs. territorial song). This is especially useful for linking acoustic activity to ecological context—for instance, certain behaviors like dawn chorus singing are tightly linked to breeding phenology and seasonal cycles in some species, so classifying detections by behavior could let you track these dynamics at scale.

However, be aware of the following:

If you try to classify detected events into behavioral categories (song vs. calls), you're implicitly assuming that the model detects all behavior types with equal sensitivity. This is almost certainly not true:

- **Loud, stereotyped songs** (e.g., territorial advertising) are typically longer, louder, and more structured, making them easier to detect and more likely to be well-represented in the model's training data.

- **Quiet contact calls or alarm calls** may be shorter, quieter, or more variable, leading to lower detection rates or higher false-negative rates. Same but more extreme goes for juvenile babbling or fledgling calls, subsong, etc.

- **Training data composition**: 'Foundation' models like Perch are trained on large but non-uniform datasets. The training corpus is skewed toward song (e.g., from crowd-sourced libraries where birders preferentially upload song), so model will often systematically under-detect calls, leading to a biased sample.

This creates some circularity of sorts: you can't estimate the true behavioral repertoire from detections alone, because the detection process itself filters the repertoire. If you then build a classifier on detected embeddings to distinguish "song" from "calls", you're training on a biased sample where song is over-represented. The resulting classifier might work well on your dataset but won't reflect true behavioral frequencies. It will still be worth doing, especially for things like woodpecker drumming vs. calls, but just be aware of the limitations.


## Temporal dynamics, ecology and song learning stuff

**Temporal and spatial dynamics**  
Track embedding centroids or cluster membership over time to quantify seasonal changes in vocal activity, migration timing, or dawn chorus composition. Map embedding clusters geographically to identify hotspots of vocal diversity or model species–environment relationships.

**Song variants and cultural change**  
You could potentially track how song types spread across the area over time using embedding-based clustering to detect variant emergence and movement. The monthly-scale data could capture some song learning and transmission dynamics – perhaps.

**Co-occurrence and interactions**  
Test for non-random temporal associations between species at sub-second to minute scales – e.g., do certain species systematically vocalize before/after others, suggesting eavesdropping, competitive displacement, heterospecific attraction/avoidance, etc.? Embeddings can facilitate rapid scanning for such patterns across massive datasets. This would need to be within sites, as clock drift would add a lot of noise across sites.

**Linking to environment and phenology**  
Compare embedding distributions, acoustic diversity, and species composition across patches in terms of tree species composition, NDVI trajectories and canopy height, temperature, to quantify how canopy composition and phenology shape the soundscape as a proxy for who’s around and when relevant behaviours occur. Combine species traits with NDVI-coupling metrics to ask which kinds of species track vegetation phenology most closely, etc.

