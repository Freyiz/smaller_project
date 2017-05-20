class WowConfig:
    factions = ['联盟', '部落']
    races = {
        '人类': '111011010111',
        '侏儒': '101011010111',
        '矮人': '111111010111',
        '暗夜精灵': '101011111101',
        '德莱尼': '111110010101',
        '狼人': '101011100111',
        '熊猫人': '100111010101',
        '兽人': '101111010110',
        '亡灵': '101011010111',
        '牛头人': '111110110001',
        '巨魔': '101111110111',
        '血精灵': '111011011111',
        '地精': '101110010111'
    }
    classes = ['战士', '圣骑士', '死亡骑士', '萨满祭司', '猎人', '盗贼', '德鲁伊', '武僧', '恶魔猎手', '法师', '术士', '牧师']
    basic = {
        '联盟': '#0078FF',
        '部落': '#B30000',
        '死亡骑士': ['#C41F3B', 'death-knight'],
        '恶魔猎手': ['#A330C9', 'demon-hunter'],
        '德鲁伊': ['#FF7D0A', 'druid'],
        '猎人': ['#ABD473', 'hunter'],
        '法师': ['#69CCF0', 'mage'],
        '武僧': ['#00FF96', 'monk'],
        '圣骑士': ['#F58CBA', 'paladin'],
        '牧师': ['#FFFFFF', 'priest'],
        '盗贼': ['#FFF569', 'rogue'],
        '萨满祭司': ['#0070DE', 'shaman'],
        '术士': ['#9482C9', 'warlock'],
        '战士': ['#C79C6E' 'warrior']
    }

    def random_player(self):
        from random import choice

        wow_class = choice(self.classes)
        races_choice = []
        for race in self.races:
            if self.races[race][self.classes.index(wow_class)] == '1':
                races_choice.append(race)
        wow_race = choice(races_choice)
        if wow_race in ['人类', '矮人', '暗夜精灵', '侏儒', '德莱尼', '狼人']:
            wow_faction = '联盟'
        elif wow_race == '熊猫人':
            wow_faction = choice(self.factions)
        else:
            wow_faction = '部落'

        return wow_faction, wow_race, wow_class