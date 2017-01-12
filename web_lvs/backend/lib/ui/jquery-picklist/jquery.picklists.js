/**
* Picklists - jQuery plugin for converting a multiple <select> into two, allowing users to easily select multiple items
* Based on code from Multiple Selects Plugin: http://code.google.com/p/jqpickLists/
*
* Copyright (c) 2007 George Smith
* Dual licensed under the MIT and GPL licenses:
* http://www.opensource.org/licenses/mit-license.php
* http://www.gnu.org/licenses/gpl.html
*
* Version: 0.1
*/

/**
* Adds multiple select behaviour to a <select> element.
* This allows options to be transferred to a different select using mouse double-clicks, or multiple options at a time via a button element.
*
* @usage
* $('#simple').pickList(options);
*/
jQuery.fn.pickList = function(settings) 
{
	// set some sensible defaults
	settings = jQuery.extend({
		buttons: true,
		removeText: 'remove',
		removeImage: '',
		addText: 'add',
		addImage: '',
		beforeFrom: '',
		beforeTo: '',
    ieBg: '',
    ieColor: 'graytext',
    testMode: false
	}, settings);
	return this.each(function() {
		if (this.multiple == false) { return; }
		var name = this.name;
		if (!this.id) {
			// we really need an id for this to work properly, so let's create one 
			// (needs error checking to see if id already exists)
			this.id = this.name.match(/[a-zA-Z0-9]+/);
		}
		var id = this.id;

		var select = jQuery('#' + id);
		
		// add onsubmit stuff to the form so all the selected elements get passed through correctly
		jQuery(this.form)
			.submit(function(e) {
				if (settings.testMode) e.preventDefault();
				for(var item = 0; item < this.pickLists.length; item++)
				{
					selectAll(this.pickLists[item]);
				}
			})
			.each(function() {
				if (this.pickLists == undefined) this.pickLists = new Array();
				// myAlert('id:' + id);
				this.pickLists.push(id);
			});

		var container = jQuery(this).parent().addClass('pickListContainer');
		
		if (settings.beforeFrom) { select.before($('<div class="pickListFrom">').text(settings.beforeFrom));}
		
    select.before($('<select id="from_' + id + '" multiple="multiple">'));
		if (settings.buttons)
		{
			select.before($('<div class="pickListButtons">')
				.append($('<button id="b_to_' + id + '">')
					.html(button(settings.addText, settings.addImage)))
				.append($('<button id="b_from_' + id + '">')
					.html(button(settings.removeText, settings.removeImage)))
			);
		}
		moveAllOptions(id, 'from_' + id);
		if (settings.beforeTo) select.before($('<div class="pickListTo>').html(settings.beforeTo));

		
		jQuery('#from_' + id).dblclick(function() { addTo('from_' + id, id); });
		jQuery('#' + id).dblclick(function() { moveFrom(id, 'from_' + id); });

		if (settings.buttons)
		{
			jQuery("#b_to_"+id).click(function(e) { e.preventDefault(); addTo('from_' + id, id); });
			jQuery("#b_from_"+id).click(function(e) { e.preventDefault(); moveFrom(id, 'from_' + id); });
		}
		if (jQuery.fn.emulateDisabled) 
      jQuery('#from_' + id).emulateDisabled();
    if (jQuery.fn.obviouslyDisabled)
      jQuery('#from_' + id).obviouslyDisabled({textColor: settings.ieColor, bgColor: settings.ieBg});
		
	});
	function button(text, image)
	{
		image = (image != '') ? '<img src="' + image + '">' : '';
		return (image + ' ' + text)
	}
	function selectAll(me) {
		$('#' + me + ' option').attr('selected', true);
		$('#from_' + me + ' option').attr('selected', false);
	}
	function addTo(from, to)
	{
		var dest = jQuery("#"+to)[0];

		jQuery("#"+from+" option:selected").clone().each(function() {
			if (this.disabled == true) return
			jQuery(this)
			.appendTo(dest)
			.attr("selected", false);
		});
		jQuery("#"+from+" option:selected")
			.attr("selected", false)
			.attr("disabled", true)
		
		if (jQuery.fn.obviouslyDisabled)
      jQuery("#"+from).obviouslyDisabled({textColor: settings.ieColor, bgColor: settings.ieBg});
	}
	function moveFrom(from, to)
	{
		var dest = jQuery("#"+to)[0];
		jQuery("#"+from+" option:selected").each(function() 
		{
			select = jQuery(this)
			val = select
				.attr("selected", false)
				.val();
			select.remove();
			jQuery('option:disabled', jQuery("#"+to)).each(function() 
			{
				if (this.value == val)
				{
					jQuery(this).attr("disabled", false);
				}
			});
		});
		
		if (jQuery.fn.obviouslyDisabled)
      jQuery("#"+to).obviouslyDisabled({textColor: settings.ieColor, bgColor: settings.ieBg});

	}
	function moveAllOptions(from, to) {
		jQuery("#"+to).html(jQuery("#"+from).html())
			.find('option:selected')
			.attr("selected", false);
		jQuery("#"+from).html('');
	}
};
