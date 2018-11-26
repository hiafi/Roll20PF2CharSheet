const attr_bonus_fields = [
        "race_bonus1", "race_bonus2", "race_bonus3", "race_penalty",
        "bg_bonus1", "bg_bonus2",
        "class1_bonus1", "class1_bonus2", "class1_bonus3", "class1_bonus4",
        "class5_bonus1", "class5_bonus2", "class5_bonus3", "class5_bonus4",
        "class10_bonus1", "class10_bonus2", "class10_bonus3", "class10_bonus4",
        "class15_bonus1", "class15_bonus2", "class15_bonus3", "class15_bonus4",
        "class20_bonus1", "class20_bonus2", "class20_bonus3", "class20_bonus4"
    ];

let change_fields="";
for (var a in attr_bonus_fields) { change_fields=change_fields+["change:", attr_bonus_fields[a], " "].join("") }

on(change_fields, function(eventInfo) {

    getAttrs(attr_bonus_fields, function(values) {
        let attrs = {
          str: 10,
          dex: 10,
          con: 10,
          int: 10,
          wis: 10,
          cha: 10
        };
        for (var attr_name in values) {
            var attr_val = values[attr_name];
            if (attr_val !== "") {
                if (attr_name === "race_penalty") {
                    attrs[attr_val] -= 2
                } else {
                    if (attrs[attr_val] >= 18) {
                        attrs[attr_val] += 1
                    }
                    else {
                        attrs[attr_val] += 2
                    }
                }
            }
        }
        console.log(attrs);

        setAttrs({
          attr_Strength_value: attrs.str,
          attr_Dexterity_value: attrs.dex,
          attr_Constitution_value: attrs.con,
          attr_Intelligence_value: attrs.int,
          attr_Wisdom_value: attrs.wis,
          attr_Charisma_value: attrs.cha
        });
   });
});
