#!/usr/bin/perl
use strict;
use warnings;
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use Module::Metadata;
use File::Find;
use Fcntl qw(:DEFAULT :flock);

use Data::Dumper;

#------------------------------------------------------------------------------------#
# Module services                                                                    #
#------------------------------------------------------------------------------------#
my $query = new CGI();
my $mname = $query->param('m');

if ($mname)
{
	print "Content-type: application/json\n\n";

	my $module = Module::Metadata->new_from_module($mname, collect_pod => 1);

	print "{ \"module\" : \"" . $module->{module} . "\", \"version\" : \"" . $module->{version} . "\"}";

	exit;
}
#------------------------------------------------------------------------------------#


#------------------------------------------------------------------------------------#
# Get the data, print the page                                                       #
#------------------------------------------------------------------------------------#
my $data = &GetData();

my $page = <<PAGE;
Cache-Control: no-store, must-revalidate
Content-type: text/html

<!doctype html>
<html lang=en>
	<head>
		<meta charset="utf-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="viewport" content="width=device-width, initial-scale=1">

		<title>Perl Development Resources</title>

		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css">
		<style>
			table, td
			{
				word-wrap: break-word;
				white-space: normal;
				min-width: 160px;
				max-width: 160px;
				cursor: default;
			}

			ul
			{
				list-style-type: none;
				padding: 0px;
				margin: 0px;
			}

			ul li
			{
				cursor: default;
				font-size: 11px;
				overflow: hidden;
				-ms-text-overflow: ellipsis;
				-o-text-overflow: ellipsis;
				text-overflow: ellipsis;
			}

			ul li span.label
			{
				font-size: 9px;
			}

			.label-as-badge
			{
				border-radius: 1em;
			}
		</style>

		<!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
		<!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
		<!--[if lt IE 9]>
			<script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
			<script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
		<![endif]-->

		<!--[if !IE]>-->
			<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
		<!--<![endif]-->

		<!--[if IE]>
			<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
		<![endif]-->

		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
		<script>
		jQuery(document).ready(function ()
		{
			var display = function ()
			{
				var el = jQuery(this);
				el.prepend('<span class="label label-info label-as-badge">' + el.attr('data-version') + '</span> ');
			}

			jQuery(".module").on('click', function ()
			{
				var version = jQuery(this).attr('data-version');

				if (version === undefined)
				{
					var el = this;

					jQuery.get("$ENV{SCRIPT_NAME}?m=" + this.title, function (data)
					{
						jQuery(el).attr('data-version', (data.version) ? data.version : 'n/a');
						display.call(el);
					});
				}
			});
		});
		</script>
	</head>
	<body>
		<nav class="navbar navbar-default" role="navigation">
			<div class="container">
				<div class="navbar-header">
					<a class="navbar-brand" href="#">Perl Development Resource</a>
				</div>
			</div>
		</nav>

		<div class="container">
			<div class="row">
				<div class="col-md-6 col-lg-6">
					<div class="panel panel-info">
						<div class="panel-heading">
							<h3 class="panel-title">Perl Information</h3>
						</div>
						<div class="panel-body">
							$data->{"info"}
						</div>
					</div>
				</div>

				<div class="col-md-6 col-lg-6">
					<div class="panel panel-primary">
						<div class="panel-heading">
							<h3 class="panel-title">Perl Environment</h3>
						</div>
						<div class="panel-body">
							$data->{"env"}
						</div>
					</div>
				</div>
			</div>

			<div class="row">
				<div class="col-md-12 col-lg-12">
					<div class="panel panel-success">
						<div class="panel-heading">
							<h3 class="panel-title">$data->{mods}->{total} Installed Perl Modules</h3>
						</div>
						<div class="panel-body">
							<div class="row">
								<div class="col-md-4 col-lg-4">
									$data->{"mods"}->{"1"}
								</div>
								<div class="col-md-4 col-lg-4">
									$data->{"mods"}->{"2"}
								</div>
								<div class="col-md-4 col-lg-4">
									$data->{"mods"}->{"3"}
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
		<script src="http://getbootstrap.com/assets/js/ie10-viewport-bug-workaround.js"></script>
	</body>
</html>
PAGE

print $page;
exit;
#------------------------------------------------------------------------------------#



#################################|     GetData     |##################################
sub GetData
{
	my $data = {};

	$data->{env}  = &GetEnvironment();
	$data->{info} = &GetInformation();
	$data->{mods} = &GetModules();

	return $data;
}
#########################################||#########################################



#############################|     GetEnvironment     |#############################
sub GetEnvironment
{
	my @table = (
		"<div class=''>",
			"\t<table class='table table-striped table-condensed table-hover'>",
				"\t\t<thead>",
					"\t\t\t<tr>",
						"\t\t\t\t<th>Key</th>",
						"\t\t\t\t<th>Value</th>",
					"\t\t\t</tr>",
				"\t\t</thead>",
				"\t\t<tbody>"
	);

	foreach my $key (sort keys %ENV)
	{
		next if ($key =~ /^(comspec|path|pathext|systemroot|windir)$/i);

		push(@table, "\t\t\t<tr>");
		push(@table, "\t\t\t\t<td>$key</td>");
		push(@table, "\t\t\t\t<td>$ENV{$key}</td>");
		push(@table, "\t\t\t</tr>");
	}

	push (@table, "\t\t<tbody>");
	push (@table, "\t</table>");
	push (@table, "</div>");

	return join("\n\t\t\t\t\t\t\t", @table);
}
#########################################||#########################################



#############################|     GetInformation     |#############################
sub GetInformation
{
	my @table = (
		"<div class=''>",
			"\t<table class='table table-striped table-hover'>",
				"\t\t<thead>",
					"\t\t\t<tr>",
						"\t\t\t\t<th>Name</th>",
						"\t\t\t\t<th>Value</th>",
					"\t\t\t</tr>",
				"\t\t</thead>",
				"\t\t<tbody>"
	);


	#-- Operating System --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$^O'>Operating System</span></td>");
	push(@table, "\t\t\t\t<td>$^O</td>");
	push(@table, "\t\t\t</tr>");


	#-- Perl Executeable --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$^X'>Perl Executeable</span></td>");
	push(@table, "\t\t\t\t<td>$^X</td>");
	push(@table, "\t\t\t</tr>");


	#-- Perl Version --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$^V'>Perl Version</span></td>");
	push(@table, "\t\t\t\t<td>$^V</td>");
	push(@table, "\t\t\t</tr>");

	#-- @INC --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\@INC'>Perl Path</span></td>");
	push(@table, "\t\t\t\t<td>" . (join("<br>", @INC)) . "</td>");
	push(@table, "\t\t\t</tr>");

	#-- Perl Locations --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td>Perl Locations</td>");
	{
		my $locations = `whereis perl`;
		$locations = ($locations) ? join('<br>', split(' ', $locations)) : "<i>not found</i>";

		push(@table, "\t\t\t\t<td>$locations</td>");
	}
	push(@table, "\t\t\t</tr>");


	#-- Sendmail Locations --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td>Sendmail Locations</td>");
	{
		my $locations = `whereis sendmail`;
		$locations = ($locations) ? join('<br>', split(' ', $locations)) : "<i>not found</i>";

		push(@table, "\t\t\t\t<td>$locations</td>");
	}
	push(@table, "\t\t\t</tr>");


	#-- CGI Version --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$CGI::VERSION'>CGI Version</span></td>");
	push(@table, "\t\t\t\t<td>" . (($CGI::VERSION) ? $CGI::VERSION : "<i>not found</i>") . "</td>");
	push(@table, "\t\t\t</tr>");


	#-- Real Group Id --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$('>Real Group Id</span></td>");
	push(@table, "\t\t\t\t<td>$(</td>");
	push(@table, "\t\t\t</tr>");


	#-- Effective Group Id --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$)'>Effective Group Id</span></td>");
	push(@table, "\t\t\t\t<td>$)</td>");
	push(@table, "\t\t\t</tr>");


	#-- Real User Id --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$<'>Real User Id</span></td>");
	push(@table, "\t\t\t\t<td>$<</td>");
	push(@table, "\t\t\t</tr>");


	#-- Effective Group Id --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$>'>Effective User Id</span></td>");
	push(@table, "\t\t\t\t<td>$></td>");
	push(@table, "\t\t\t</tr>");


	#-- Process Id --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$\$'>Process Id</span></td>");
	push(@table, "\t\t\t\t<td>$$</td>");
	push(@table, "\t\t\t</tr>");


	#-- Program Name --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$0'>Program Name</span></td>");
	push(@table, "\t\t\t\t<td>$0</td>");
	push(@table, "\t\t\t</tr>");


	#-- Base Time --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$^T'>Base Time</span></td>");
	push(@table, "\t\t\t\t<td>$^T</td>");
	push(@table, "\t\t\t</tr>");


	#-- Default Autoflush --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$|'>Default Autoflush</span></td>");
	push(@table, "\t\t\t\t<td>$|</td>");
	push(@table, "\t\t\t</tr>");


	#-- Warning Switch --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$^W'>Warning Switch</span></td>");
	push(@table, "\t\t\t\t<td>$^W</td>");
	push(@table, "\t\t\t</tr>");


	#-- Taint Mode --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\${^TAINT}'>Taint Mode</span></td>");
	push(@table, "\t\t\t\t<td>${^TAINT}</td>");
	push(@table, "\t\t\t</tr>");


	#-- Debugging Flag --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$^D'>Debugging Flag</span></td>");
	push(@table, "\t\t\t\t<td>$^D</td>");
	push(@table, "\t\t\t</tr>");


	#-- Debugging Support --#
	push(@table, "\t\t\t<tr>");
	push(@table, "\t\t\t\t<td><span title='\$^P'>Debugging Support</span></td>");
	push(@table, "\t\t\t\t<td>$^P</td>");
	push(@table, "\t\t\t</tr>");


	push (@table, "\t\t<tbody>");
	push (@table, "\t</table>");
	push (@table, "</div>");

	return join("\n\t\t\t\t\t\t\t", @table);
}
#########################################||#########################################



###############################|     GetModules     |###############################
sub GetModules
{
	my %modules;
	find(
	{
		untaint => 1,
		untaint_pattern => qr|^(.+)$|,
		wanted => sub
		{
			if ($_ =~ /\.pm$/i)
			{
				my $file = $1 if ($File::Find::name =~ /^(.+)$/);

				open(FILE, $file) || return;
				flock (FILE, LOCK_SH);
				while (my $line = <FILE>)
				{
					if ($line =~ /^ *package +(\S+);/)
					{
						$modules{$1} = 1 unless ($1 =~ /^_/);
						last;
					}
				}
				close(FILE);
			}
		}
	}, @INC);


	my @modules = sort {lc($a) cmp lc($b)} keys %modules;
	my $modules = { total =>  scalar @modules };

	use integer;
	my $percol = $modules->{total} / 3;
	my $ovrflw = $modules->{total} % 3;

	for (my $i = 0; $i < 3; $i += 1)
	{
		my @column = splice(@modules, 0, ($ovrflw > $i) ? $percol + 1 : $percol);
		@column = map { "<li class='module' id='$_' title='$_'>$_</li>" } @column;
		$modules->{$i + 1} = "<ul>" . (join('', @column)) . "</ul>";
	}

	return $modules;
}
#########################################||#########################################
