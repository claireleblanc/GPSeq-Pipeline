#!/usr/bin/Rscript

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 2.0.0
# Description: filter and deduplicate UMIs
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

suppressMessages(require(argparser))
suppressMessages(require(cowplot))
suppressMessages(require(data.table))
suppressMessages(require(ggplot2))
suppressMessages(require(pbapply))
theme_set(theme_cowplot())
pboptions(type="timer")

# INPUT ========================================================================

# Create arguent parser
parser = arg_parser('Deduplicate UMIs.', name = 'umi_dedupl.R')

# Define mandatory arguments
parser = add_argument(parser, arg = 'input',
	help = 'Path to chrom|pos|seqs|quals file.')
parser = add_argument(parser, arg = 'output',
	help = 'Path to output file.')

# Define elective arguments
parser = add_argument(parser, arg = '--num-proc', short = '-c',
	help = 'Number of cores for parallel computation.',
	default = 1, type = class(0))
parser = add_argument(parser, arg = '--num-reg', short = '-r',
	help = 'Number of regions per job during parallel computation.',
	default = 1000, type = class(0))

# Parse arguments
p = parse_args(parser)

# Attach argument values to variables
attach(p['' != names(p)])

setDTthreads(num_proc)

# RUN ==========================================================================

# Read UMI file ----------------------------------------------------------------

cat(' · Reading UMIs ...\n')
u <- fread(input, col.names=c('chr', 'pos', 'seq', 'qual'),
	       nThread=num_proc, showProgress=T)

cat(' >>> Pre-processing ...\n')
u$seq = pblapply(u$seq,
	             function(x) unlist(strsplit(x, " ", fixed = T)),
	             cl = num_proc)
u$n = unlist(pblapply(u$seq, length, cl = num_proc))
u[, qual := NULL]

# Initialize -------------------------------------------------------------------

# Check UMI length
cat(' · Checking UMI length ...\n')

ulen = unique(nchar(unique(unlist(u$seq))))

if ( 1 < length(ulen) ) {
	cat(paste0('  >> Multiple UMI length detected: ',
		paste(ulen, collapse = ' '), ' [nt]\n'))
	cat(paste0('  >> Using the average to calculate the threshold: ',
		mean(ulen), ' [nt]\n'))
} else {
	cat(paste0('  >> UMI length is consistently ', ulen, ' nt.\n'))
}

# Count UMIs
cat(' · Counting UMIs ...\n')
log = paste0(u[, sum(n)], ' non-orphan reads.\n')

# Strict unique ----------------------------------------------------------------

# Perform strict unique
cat(' · Performing strict UMI deduplication...\n')
u$group = findInterval(seq(1, nrow(u)), seq(1, nrow(u), by = num_reg))
u = rbindlist(pblapply(split(u, u$group), function(rowList, maxGroup) {
	# cat(sprintf("%d/%d (%.2f%%)\n", rowList[1, group], maxGroup,
	# 	rowList[1, group]/maxGroup*100))
	rowList[, group := NULL]
	out = rbindlist(lapply(split(rowList, 1:nrow(rowList)), function(row) {
		uniqSeq = unique(unlist(row$seq))
		out = data.table(
			chr = row$chr,
			pos = row$pos,
			seq = list(uniqSeq),
			preN = row$n,
			postN = length(uniqSeq)
		)
		unlink(uniqSeq)
		unlink(row)
		return(out)
	}))
	unlink(rowList)
	return(out)
}, u[, max(group)], cl = num_proc))

nu = u[, sum(preN)]
nurm = u[, sum(preN-postN)]
nuk = u[, sum(postN)]
cat(sprintf(' >>> %d (%.2f%%) UMIs identified as duplicates and removed.\n',
	nurm, nurm/nu*100))
log=sprintf('%s%d (%.2f%%) duplicated UMIs.\n%d UMIs left after deduplication.\n',
	log, nurm, nurm/nu*100, nuk)
cat(sprintf(' >>> Remaining UMIs: %d\n', nuk))

# Export deduplicated UMIs -----------------------------------------------------

setnames(u, "postN", "counts")
u[, preN := NULL]
u$seq = unlist(lapply(u$seq, paste, collapse = " "))
cat(' · Saving de-duplicated UMI list ...\n')
fwrite(as.matrix(u), output,
	row.names = F, col.names = F, sep = '\t', quote = F)

# Write log --------------------------------------------------------------------

logfile = file.path(dirname(output), sprintf('%s.umi_prep_notes.txt', basename(input)))
log = unlist(strsplit(log, '\n', fixed = T))
write.table(log, logfile, row.names = F, col.names = F, quote = F, append = T)

# END --------------------------------------------------------------------------

################################################################################

