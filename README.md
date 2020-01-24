# article-regions
A dataset of region-annotated scientific articles from PubMed Central, for document layout analysis/segmentation.

## Regions
Nine document regions are annotated:
* Title
* Authors
* Abstract
* Body
* Figure
* Figure Caption
* Table
* Table Caption
* References

## Getting and preparing documents

A script is included to download the corresponding article PDFs from PubMed Central, as well as render the article pages to JPG images. Some Linux utilities are used: curl, pdfinfo (from poppler-utils), and convert (from imagemagick). Note that by default ImageMagick disables support for PDF files, but this can easily be fixed by updating its policy file:
```
sudo sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml
```

## Citation
C.X. Soto and S.J. Yoo, "Visual Detection with Context for Document Layout Analysis", _proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing_ (EMNLP-IJCNLP), 2019.

https://www.aclweb.org/anthology/D19-1348.pdf
