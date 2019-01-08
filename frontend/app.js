/**
 * Controllers for the buttons and variables.
 */
$(function(){
    $('.start-genetic-algorithm').click(function(){
        $(this).hide();
        $('.pause-genetic-algorithm').show();
        testGeneticKitchen.autoGenerate = true;
        testGeneticKitchen.nextGeneration();
        return false;
    });

    $('.pause-genetic-algorithm').click(function(){
        testGeneticKitchen.autoGenerate = false;
        $(this).hide();
        $('.start-genetic-algorithm').show();
        return false;
    });

    $('.step-genetic-algorithm').click(function(){
        testGeneticKitchen.nextGeneration();
        return false;
    });

    $('.reset-genetic-algorithm').click(function(){
        testGeneticKitchen.reset();
        testGeneticKitchen.render();
        return false;
    });

    $('.death-rate').change(function(){
        testGeneticKitchen.deathRate = Number($(this).val());
    });

    $('.population').change(function(){
        testGeneticKitchen.populationSize = Number($(this).val());
    });

    $('.mutation-probability').change(function(){
        testGeneticKitchen.mutationProbability = Number($(this).val());
    });

    $('.mutation-multiplier').change(function(){
        testGeneticKitchen.mutationMultiplier = Number($(this).val());
    });

    testGeneticKitchen.render();
});
